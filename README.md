# JARVIS Arduino Display — V2

Mini interface física do JARVIS usando:
- Arduino Uno
- OLED I2C 128x64 (provável SSD1306)
- Desktop Windows 11 como ponte
- Controle local e pela rede local

---

## Visão geral

Arquitetura:

`MacBook / JARVIS -> rede local -> Windows 11 -> USB serial -> Arduino Uno -> OLED`

Na prática:
- o **Arduino** desenha a interface na OLED
- o **Windows 11** roda uma ponte em Python
- a ponte recebe comandos HTTP e envia pela serial para o Arduino
- a V2 permite **controle pela rede local**
- a V2 suporta **token opcional** para proteger a API

---

## Arquivos do projeto

- `jarvis_display.ino` -> sketch do Arduino
- `bridge_windows.py` -> ponte HTTP -> Serial no Windows
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

## Passo a passo completo — Arduino

### 1) Abrir o projeto
Abra o arquivo:

- `jarvis_display.ino`

### 2) Selecionar a placa
Na Arduino IDE:
- **Board / Placa**: `Arduino Uno`

### 3) Selecionar a porta
Escolha a porta COM correspondente ao Arduino.

### 4) Fazer upload
Clique em **Upload**.

### 5) Resultado esperado
Se tudo estiver certo, a OLED deve:
- mostrar a tela de boot do JARVIS
- depois ir para a tela `ONLINE`

### 6) Se não funcionar
Se a tela não acender ou nada aparecer:
- revise os fios `SDA` e `SCL`
- confirme se `A4 = SDA` e `A5 = SCL`
- teste trocar no código:

```cpp
#define SCREEN_ADDRESS 0x3C
```

para:

```cpp
#define SCREEN_ADDRESS 0x3D
```

---

## Passo a passo completo — Windows 11

### 1) Clonar o repositório

```powershell
git clone https://github.com/Andrelealx/jarvis-arduino-display.git
cd jarvis-arduino-display
```

### 2) Verificar Python

```powershell
python --version
```

Se não tiver Python 3 instalado, instale antes.

### 3) Instalar dependências

```powershell
pip install -r requirements.txt
```

### 4) Descobrir a porta COM do Arduino
Você pode verificar no Arduino IDE ou no Gerenciador de Dispositivos.

Exemplo comum:
- `COM3`
- `COM4`
- `COM5`

### 5) Descobrir o IP local do Windows
No PowerShell:

```powershell
ipconfig
```

Procure o IPv4 da máquina. Exemplo:
- `192.168.1.50`

### 6) Rodar a ponte
Exemplo simples:

```powershell
python bridge_windows.py --port COM5 --api-port 8765
```

Exemplo recomendado com token:

```powershell
python bridge_windows.py --port COM5 --api-port 8765 --token jarvis123
```

Troque `COM5` pela porta real do Arduino.

### 7) Resultado esperado
Se deu tudo certo, o terminal deve mostrar algo como:

```powershell
JARVIS bridge online on http://0.0.0.0:8765 -> COM5
API token protection: ENABLED
```

---

## Validação local

### 1) Teste de saúde da API

```powershell
curl http://localhost:8765/health
```

Resultado esperado: resposta JSON com `ok: true`.

### 2) Colocar a tela em modo online

Sem token:

```powershell
curl -X POST http://localhost:8765/online
```

Com token:

```powershell
curl -X POST http://localhost:8765/online -H "X-API-Key: jarvis123"
```

### 3) Mostrar relógio

Sem token:

```powershell
curl -X POST http://localhost:8765/clock -H "Content-Type: application/json" -d '{"time":"03:49","subtitle":"Windows Link OK"}'
```

Com token:

```powershell
curl -X POST http://localhost:8765/clock -H "Content-Type: application/json" -H "X-API-Key: jarvis123" -d '{"time":"03:49","subtitle":"Windows Link OK"}'
```

### 4) Mostrar mensagem

Sem token:

```powershell
curl -X POST http://localhost:8765/message -H "Content-Type: application/json" -d '{"line1":"JARVIS","line2":"Sistema OK","line3":"Andre online"}'
```

Com token:

```powershell
curl -X POST http://localhost:8765/message -H "Content-Type: application/json" -H "X-API-Key: jarvis123" -d '{"line1":"JARVIS","line2":"Sistema OK","line3":"Andre online"}'
```

### 5) Mostrar alerta temporário

Sem token:

```powershell
curl -X POST http://localhost:8765/alert -H "Content-Type: application/json" -d '{"text":"Nova mensagem"}'
```

Com token:

```powershell
curl -X POST http://localhost:8765/alert -H "Content-Type: application/json" -H "X-API-Key: jarvis123" -d '{"text":"Nova mensagem"}'
```

### 6) Colocar em idle

Sem token:

```powershell
curl -X POST http://localhost:8765/idle
```

Com token:

```powershell
curl -X POST http://localhost:8765/idle -H "X-API-Key: jarvis123"
```

---

## Validação pela rede local

Suponha que o IP do Windows seja `192.168.1.50`.

### Teste do MacBook para o Windows

Sem token:

```bash
curl http://192.168.1.50:8765/health
```

Com token em endpoint protegido:

```bash
curl -X POST http://192.168.1.50:8765/message \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: jarvis123' \
  -d '{"line1":"JARVIS","line2":"Controle remoto","line3":"MacBook OK"}'
```

Se isso funcionar, a ponte está acessível na rede local e pronta para integração maior.

---

## Endpoints disponíveis

### `GET /health`
Verifica se a ponte está online.

### `POST /online`
Coloca a tela no modo online.

### `POST /idle`
Coloca a tela no modo idle.

### `POST /clock`
Mostra relógio.

Exemplo:

```json
{
  "time": "03:49",
  "subtitle": "Windows 11"
}
```

### `POST /message`
Mostra mensagem em 2 ou 3 linhas.

Exemplo:

```json
{
  "line1": "JARVIS",
  "line2": "Sistema OK",
  "line3": "Andre online"
}
```

### `POST /alert`
Mostra um alerta temporário.

Exemplo:

```json
{
  "text": "Nova mensagem"
}
```

---

## Segurança básica da V2

A API pode rodar com token opcional.

### Como habilitar

```powershell
python bridge_windows.py --port COM5 --api-port 8765 --token jarvis123
```

Depois, envie o header:

```http
X-API-Key: jarvis123
```

ou:

```http
Authorization: Bearer jarvis123
```

### Recomendação
Use token sempre que a API estiver exposta na rede local.

---

## Firewall do Windows

Se o MacBook não conseguir acessar a API do Windows pela rede local, talvez o Windows Firewall esteja bloqueando.

Verifique se a porta `8765` está liberada para a rede local privada.

Se necessário, crie uma regra liberando entrada TCP nessa porta.

---

## Solução de problemas

### A API responde localmente, mas não responde de outro computador
Possíveis causas:
- firewall do Windows
- IP errado
- máquina em outra rede/sub-rede
- antivírus bloqueando

Checklist:
- confirmar `ipconfig`
- confirmar porta `8765`
- testar `curl http://IP_DO_WINDOWS:8765/health`
- revisar firewall

### A API responde, mas a tela não muda
Possíveis causas:
- porta COM errada
- sketch não foi gravado no Arduino
- OLED em endereço I2C diferente (`0x3D` em vez de `0x3C`)
- fios SDA/SCL invertidos

Checklist:
- confirmar upload do `.ino`
- confirmar COM correta
- revisar A4/A5
- testar `0x3D`

### O script Python não abre a serial
Possíveis causas:
- COM errada
- Arduino IDE/Serial Monitor ainda aberto travando a porta
- cabo USB com falha

Ações:
- fechar Arduino IDE ou Serial Monitor
- testar outra porta COM
- reconectar o USB

### Recebo erro 401 unauthorized
Possíveis causas:
- token errado
- header ausente
- token diferente do configurado no processo Python

Ações:
- revisar `--token`
- reenviar com `X-API-Key`
- confirmar se reiniciou a ponte com o token esperado

---

## Fluxo recomendado de uso

1. Fazer upload do sketch no Arduino
2. Rodar `bridge_windows.py` no Windows
3. Testar `/health`
4. Testar `/online`
5. Testar `/message`
6. Testar `/alert`
7. Confirmar que a OLED responde corretamente
8. Descobrir IP local do Windows
9. Testar chamada do MacBook para o Windows
10. Validar proteção com token

---

## Visual da interface

A interface atual inclui:
- boot screen
- online screen
- clock screen
- message screen
- alert overlay
- idle screen

Estilo:
- moldura estilo painel
- cabeçalho `JARVIS // ...`
- visual minimalista futurista

---

## Próximas evoluções sugeridas

- auto-start da ponte no Windows
- integração direta com eventos reais do JARVIS
- menus com botão físico
- ícones customizados
- animações melhores
- sensor de presença / brilho
- modo status do desktop
- serviço em background no Windows
- autenticação mais forte

---

## Repositório oficial

GitHub:

<https://github.com/Andrelealx/jarvis-arduino-display>
