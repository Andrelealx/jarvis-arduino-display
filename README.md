# JARVIS Arduino Display — V3

Mini interface física do JARVIS usando:
- Arduino Uno
- OLED I2C 128x64 (provável SSD1306)
- Desktop Windows 11 como ponte
- Controle local e pela rede local
- Modo autonômico por polling remoto

---

## Visão geral

Arquitetura base:

`MacBook / JARVIS -> rede local -> Windows 11 -> USB serial -> Arduino Uno -> OLED`

Arquitetura autonômica V3:

`JARVIS -> JSON remoto -> Windows poller -> bridge local -> Arduino -> OLED`

Na prática:
- o **Arduino** desenha a interface na OLED
- o **Windows 11** roda uma ponte em Python
- o **poller** no Windows consulta um JSON remoto periodicamente
- quando encontra novos comandos, aplica na tela automaticamente

Isso resolve a autonomia prática quando o agente não consegue chamar diretamente um IP privado da sua LAN.

---

## Arquivos do projeto

- `jarvis_display.ino` -> sketch do Arduino
- `bridge_windows.py` -> ponte HTTP -> Serial no Windows
- `state_poller.py` -> poller que lê comandos remotos
- `command_state.example.json` -> exemplo do JSON remoto
- `command_state.json` -> estado remoto pronto para uso
- `requirements.txt` -> dependências Python

---

## Hardware esperado

### Ligações do OLED no Arduino Uno

- `GND -> GND`
- `VCC -> 5V`
- `SDA -> A4`
- `SCL -> A5`

> Observação: a maioria desses displays OLED I2C funciona em `0x3C`. Se não funcionar, teste `0x3D` no arquivo `jarvis_display.ino`.

---

## Bibliotecas Arduino

Instale pela Arduino IDE:
- **Adafruit GFX Library**
- **Adafruit SSD1306**

---

## Passo a passo — Arduino

1. Abra `jarvis_display.ino`
2. Selecione a placa `Arduino Uno`
3. Selecione a porta COM
4. Faça upload
5. Confirme que a OLED mostra boot e depois `ONLINE`

Se não funcionar, revise fios e teste `0x3D` em vez de `0x3C`.

---

## Passo a passo — Windows 11

### 1) Clonar o repositório

```powershell
git clone https://github.com/Andrelealx/jarvis-arduino-display.git
cd jarvis-arduino-display
```

### 2) Instalar dependências

```powershell
pip install -r requirements.txt
```

### 3) Rodar a bridge local

Exemplo com COM4 e token:

```powershell
python bridge_windows.py --port COM4 --api-port 8765 --token jarvis123
```

### 4) Testar localmente

```powershell
curl http://localhost:8765/health
```

---

## V2 — Controle direto pela rede local

Se o IP do Windows for `192.168.0.13`, você pode chamar:

```bash
curl http://192.168.0.13:8765/health
```

Exemplo de mensagem:

```bash
curl -X POST http://192.168.0.13:8765/message \
  -H 'Content-Type: application/json' \
  -d '{"line1":"JARVIS","line2":"Controle remoto","line3":"MacBook OK"}'
```

Se a bridge estiver com token:

```bash
curl -X POST http://192.168.0.13:8765/message \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: jarvis123' \
  -d '{"line1":"JARVIS","line2":"Protegido","line3":"Rede local"}'
```

---

## V3 — Modo autonômico por polling

### Ideia
Em vez de depender de `curl` manual, o Windows roda um processo que lê um JSON remoto de tempos em tempos.

Quando surgem comandos novos nesse JSON, o poller envia esses comandos para a bridge local, e a tela muda sozinha.

### JSON remoto pronto
Já existe um arquivo pronto no repositório:

- `command_state.json`

URL raw esperada:

```text
https://raw.githubusercontent.com/Andrelealx/jarvis-arduino-display/main/command_state.json
```

### Conteúdo inicial atual
O `command_state.json` já foi criado com comandos iniciais de validação autonômica.

### Tipos de comando suportados
- `online`
- `idle`
- `message`
- `alert`
- `clock`

### Campos por tipo

#### `online`
```json
{ "id": "x1", "type": "online" }
```

#### `idle`
```json
{ "id": "x2", "type": "idle" }
```

#### `message`
```json
{
  "id": "x3",
  "type": "message",
  "line1": "JARVIS",
  "line2": "Nova tarefa",
  "line3": "Andre"
}
```

#### `alert`
```json
{
  "id": "x4",
  "type": "alert",
  "text": "Nova mensagem"
}
```

#### `clock`
```json
{
  "id": "x5",
  "type": "clock",
  "subtitle": "Windows 11"
}
```

---

## Como subir o modo autonômico

### 1) Rodar a bridge local

```powershell
python bridge_windows.py --port COM4 --api-port 8765 --token jarvis123
```

### 2) Rodar o poller

```powershell
python state_poller.py --state-url https://raw.githubusercontent.com/Andrelealx/jarvis-arduino-display/main/command_state.json --bridge-url http://127.0.0.1:8765 --bridge-token jarvis123 --shared-token change-me --interval 5
```

### 3) O que o poller faz
- lê o JSON remoto
- verifica o token compartilhado
- ignora comandos já aplicados
- aplica apenas comandos novos
- salva cache local em `.poller_state.json`

---

## Como operar a tela de forma autonômica

O caminho prático é:
1. manter `command_state.json` no repositório
2. adicionar novos comandos com IDs novos
3. dar commit e push
4. o poller no Windows detecta e aplica sozinho

Exemplo de JSON:

```json
{
  "updatedAt": "2026-04-03T04:40:00-03:00",
  "token": "change-me",
  "commands": [
    {
      "id": "msg-20260403-0440-001",
      "type": "message",
      "line1": "JARVIS",
      "line2": "Modo autonomo",
      "line3": "Ativado"
    },
    {
      "id": "alert-20260403-0440-001",
      "type": "alert",
      "text": "Nova ordem"
    }
  ]
}
```

### Regra importante
Para o poller aplicar algo novo, cada comando precisa ter um **ID novo**.

---

## Segurança da V3

A V3 tem dois níveis simples de proteção:

### 1) Token da bridge local
Usado para proteger a API do Windows.

Exemplo:

```powershell
python bridge_windows.py --port COM4 --api-port 8765 --token jarvis123
```

### 2) Shared token no JSON remoto
O poller valida o campo `token` do JSON remoto antes de aplicar comandos.

Exemplo no JSON:

```json
{
  "token": "change-me"
}
```

Exemplo no poller:

```powershell
python state_poller.py --state-url URL --shared-token change-me
```

---

## Solução de problemas

### O poller não aplica nada
Possíveis causas:
- URL do JSON errada
- JSON inválido
- token compartilhado divergente
- bridge local offline

Checklist:
- abrir a URL no navegador
- validar JSON
- conferir `--shared-token`
- conferir `http://127.0.0.1:8765/health`

### Comando já foi executado e não repete
Isso é esperado.

O poller deduplica por `id`.

Se quiser reaplicar, crie um novo comando com **novo ID**.

### Bridge responde, mas a OLED não muda
Checklist:
- confirmar COM correta
- confirmar sketch no Arduino
- revisar SDA/A4 e SCL/A5
- testar `0x3D`

---

## Fluxo recomendado

### V1
- validar hardware e OLED

### V2
- validar bridge local e controle pela LAN

### V3
- subir bridge
- subir poller
- atualizar `command_state.json`
- dar commit/push
- deixar o Windows aplicar sozinho

---

## Próximas evoluções sugeridas

- auto-start da bridge no Windows
- auto-start do poller no Windows
- endpoint de confirmação/ack de comando
- fila com expiração
- prioridade de comandos
- páginas rotativas automáticas
- integração com eventos reais do JARVIS
- serviço Windows em background

---

## Repositório oficial

GitHub:

<https://github.com/Andrelealx/jarvis-arduino-display>
