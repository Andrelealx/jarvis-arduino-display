# JARVIS Arduino Display — V1

Mini interface física do JARVIS usando:
- Arduino Uno
- OLED I2C 128x64 (provável SSD1306)
- Desktop Windows 11 como ponte

---

## Visão geral

Arquitetura:

`MacBook / JARVIS -> rede local -> Windows 11 -> USB serial -> Arduino Uno -> OLED`

Na prática:
- o **Arduino** desenha a interface na OLED
- o **Windows 11** roda uma ponte em Python
- a ponte recebe comandos HTTP e envia pela serial para o Arduino

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

### 5) Rodar a ponte
Exemplo:

```powershell
python bridge_windows.py --port COM5 --api-port 8765
```

Troque `COM5` pela porta real do Arduino.

### 6) Resultado esperado
Se deu tudo certo, o terminal deve mostrar algo como:

```powershell
JARVIS bridge online on http://0.0.0.0:8765 -> COM5
```

---

## Validação completa

### 1) Teste de saúde da API

```powershell
curl http://localhost:8765/health
```

Resultado esperado: resposta JSON com `ok: true`.

### 2) Colocar a tela em modo online

```powershell
curl -X POST http://localhost:8765/online
```

Resultado esperado:
- tela `JARVIS // ONLINE`

### 3) Mostrar relógio

```powershell
curl -X POST http://localhost:8765/clock -H "Content-Type: application/json" -d '{"time":"03:49","subtitle":"Windows Link OK"}'
```

Resultado esperado:
- tela de relógio
- subtítulo com status

### 4) Mostrar mensagem

```powershell
curl -X POST http://localhost:8765/message -H "Content-Type: application/json" -d '{"line1":"JARVIS","line2":"Sistema OK","line3":"Andre online"}'
```

Resultado esperado:
- tela de mensagem

### 5) Mostrar alerta temporário

```powershell
curl -X POST http://localhost:8765/alert -H "Content-Type: application/json" -d '{"text":"Nova mensagem"}'
```

Resultado esperado:
- alerta temporário por alguns segundos

### 6) Colocar em idle

```powershell
curl -X POST http://localhost:8765/idle
```

Resultado esperado:
- tela de descanso

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

## Solução de problemas

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

### A OLED não acende
Possíveis causas:
- alimentação errada
- GND/VCC invertidos
- módulo com outro controlador/endereço

Ações:
- revisar ligação elétrica
- testar `0x3D`
- confirmar compatibilidade SSD1306

---

## Fluxo recomendado de uso

1. Fazer upload do sketch no Arduino
2. Rodar `bridge_windows.py` no Windows
3. Testar `/health`
4. Testar `/online`
5. Testar `/message`
6. Testar `/alert`
7. Confirmar que a OLED responde corretamente

---

## Visual da V1

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
- controle remoto pela rede local
- integração com eventos reais do JARVIS
- menus com botão físico
- ícones customizados
- animações melhores
- sensor de presença / brilho
- modo status de sistema do desktop

---

## Repositório oficial

GitHub:

<https://github.com/Andrelealx/jarvis-arduino-display>
