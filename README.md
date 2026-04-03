# JARVIS Arduino Display — V1

V1 de uma mini interface física do JARVIS usando:
- Arduino Uno
- OLED I2C 128x64 (provável SSD1306)
- Desktop Windows 11 como ponte

## Arquitetura

MacBook / JARVIS -> rede local -> Windows 11 -> USB serial -> Arduino Uno -> OLED

## Arquivos

- `jarvis_display.ino` -> sketch do Arduino
- `bridge_windows.py` -> ponte HTTP -> Serial no Windows
- `requirements.txt` -> dependências Python

## Ligações esperadas

- GND -> GND
- VCC -> 5V
- SDA -> A4
- SCL -> A5

## Bibliotecas Arduino

Instalar pela Arduino IDE:
- Adafruit GFX Library
- Adafruit SSD1306

## Subir no Arduino

1. Abrir `jarvis_display.ino` na Arduino IDE
2. Selecionar placa `Arduino Uno`
3. Selecionar a porta COM correta
4. Fazer upload

Se o display não iniciar, testar o endereço I2C `0x3D` no lugar de `0x3C`.

## Subir no Windows 11

1. Instalar Python 3
2. Abrir PowerShell na pasta do projeto
3. Instalar dependências:

```powershell
pip install -r requirements.txt
```

4. Rodar a ponte:

```powershell
python bridge_windows.py --port COM5 --api-port 8765
```

Troque `COM5` pela porta real do Arduino.

## Testes rápidos

### Saúde

```powershell
curl http://localhost:8765/health
```

### Colocar online

```powershell
curl -X POST http://localhost:8765/online
```

### Tela de relógio

```powershell
curl -X POST http://localhost:8765/clock -H "Content-Type: application/json" -d '{"time":"03:49","subtitle":"Windows Link OK"}'
```

### Mensagem

```powershell
curl -X POST http://localhost:8765/message -H "Content-Type: application/json" -d '{"line1":"JARVIS","line2":"Sistema OK","line3":"Andre online"}'
```

### Alerta

```powershell
curl -X POST http://localhost:8765/alert -H "Content-Type: application/json" -d '{"text":"Nova mensagem"}'
```

## Estilo visual da V1

- Boot screen
- Online screen
- Clock screen
- Message screen
- Alert overlay
- Idle screen

## Próximas evoluções sugeridas

- Auto-start no Windows
- Integração com eventos reais do JARVIS
- Menus via botão físico
- Ícones customizados
- Animações mais sofisticadas
- Sensor de presença / brilho
