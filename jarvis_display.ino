#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

String currentScreen = "boot";
String line1 = "JARVIS";
String line2 = "Inicializando";
String line3 = "";
String alertText = "";
unsigned long alertUntil = 0;
unsigned long lastAnim = 0;
unsigned long bootStart = 0;
unsigned long lastClockTick = 0;
int pulseFrame = 0;
int bootDots = 0;
bool dirty = true;

void centerText(const String &text, int y, int size) {
  int16_t x1, y1;
  uint16_t w, h;
  display.setTextSize(size);
  display.getTextBounds(text, 0, y, &x1, &y1, &w, &h);
  int x = (SCREEN_WIDTH - w) / 2;
  if (x < 0) x = 0;
  display.setCursor(x, y);
  display.print(text);
}

void drawFrame() {
  display.drawRoundRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 6, SSD1306_WHITE);
  display.drawRoundRect(3, 3, SCREEN_WIDTH - 6, SCREEN_HEIGHT - 6, 4, SSD1306_WHITE);
}

void drawHeader(const String &title) {
  display.fillRect(6, 6, SCREEN_WIDTH - 12, 12, SSD1306_WHITE);
  display.setTextColor(SSD1306_BLACK);
  display.setTextSize(1);
  display.setCursor(10, 8);
  display.print(title);
  display.setTextColor(SSD1306_WHITE);
}

void renderBoot() {
  display.clearDisplay();
  drawFrame();
  drawHeader("JARVIS // BOOT");
  centerText("JARVIS", 22, 2);
  display.setTextSize(1);
  centerText("Inicializando", 46, 1);
  display.setCursor(92, 46);
  for (int i = 0; i < bootDots; i++) display.print('.');
  display.display();
}

void renderOnline() {
  display.clearDisplay();
  drawFrame();
  drawHeader("JARVIS // ONLINE");
  centerText("ONLINE", 20, 2);

  // Indicador grande e inequívoco
  display.drawCircle(18, 49, 7, SSD1306_WHITE);
  if (pulseFrame % 2 == 0) {
    display.fillCircle(18, 49, 5, SSD1306_WHITE);
  }

  // Barra de pulso visível
  int barWidth = (pulseFrame % 2 == 0) ? 40 : 18;
  display.drawRect(30, 44, 48, 10, SSD1306_WHITE);
  display.fillRect(34, 47, barWidth, 4, SSD1306_WHITE);

  display.setTextSize(1);
  display.setCursor(84, 46);
  display.print("OK");
  display.setCursor(30, 58);
  display.print("Link Windows");
  display.display();
}

void renderMessage() {
  display.clearDisplay();
  drawFrame();
  drawHeader("JARVIS // MSG");
  display.setTextSize(2);
  display.setCursor(10, 22);
  display.print(line1);
  display.setTextSize(1);
  display.setCursor(10, 46);
  display.print(line2);
  if (line3.length() > 0) {
    display.setCursor(10, 56);
    display.print(line3);
  }
  display.display();
}

void renderClock() {
  display.clearDisplay();
  drawFrame();
  drawHeader("JARVIS // TIME");
  centerText(line1, 22, 2);
  centerText(line2, 46, 1);
  display.display();
}

void renderAlert() {
  display.clearDisplay();
  drawFrame();
  drawHeader("JARVIS // ALERTA");
  centerText("ALERTA", 20, 2);
  display.setTextSize(1);
  display.setCursor(10, 46);
  display.print(alertText);
  display.display();
}

void renderIdle() {
  display.clearDisplay();
  drawFrame();
  drawHeader("JARVIS // IDLE");
  centerText("Andre", 22, 2);
  display.setTextSize(1);
  centerText("Sistema operacional", 46, 1);
  display.display();
}

void renderCurrent() {
  if (millis() < alertUntil && alertText.length() > 0) {
    renderAlert();
    dirty = false;
    return;
  }

  if (currentScreen == "boot") renderBoot();
  else if (currentScreen == "online") renderOnline();
  else if (currentScreen == "msg") renderMessage();
  else if (currentScreen == "clock") renderClock();
  else if (currentScreen == "idle") renderIdle();
  else renderOnline();

  dirty = false;
}

void handleCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  if (cmd.startsWith("SCREEN:")) {
    currentScreen = cmd.substring(7);
    dirty = true;
  } else if (cmd.startsWith("LINE1:")) {
    line1 = cmd.substring(6);
    dirty = true;
  } else if (cmd.startsWith("LINE2:")) {
    line2 = cmd.substring(6);
    dirty = true;
  } else if (cmd.startsWith("LINE3:")) {
    line3 = cmd.substring(6);
    dirty = true;
  } else if (cmd.startsWith("MSG:")) {
    currentScreen = "msg";
    String payload = cmd.substring(4);
    int sep = payload.indexOf('|');
    if (sep >= 0) {
      line1 = payload.substring(0, sep);
      line2 = payload.substring(sep + 1);
    } else {
      line1 = payload;
      line2 = "";
    }
    dirty = true;
  } else if (cmd.startsWith("TIME:")) {
    currentScreen = "clock";
    line1 = cmd.substring(5);
    dirty = true;
  } else if (cmd.startsWith("SUB:")) {
    line2 = cmd.substring(4);
    dirty = true;
  } else if (cmd.startsWith("ALERT:")) {
    alertText = cmd.substring(6);
    alertUntil = millis() + 8000;
    dirty = true;
  } else if (cmd == "CLEAR") {
    line1 = "";
    line2 = "";
    line3 = "";
    currentScreen = "idle";
    dirty = true;
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    for (;;) {}
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  bootStart = millis();
  dirty = true;
  renderCurrent();
}

void loop() {
  while (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    handleCommand(cmd);
  }

  unsigned long now = millis();

  if (currentScreen == "boot" && now - bootStart > 4000) {
    currentScreen = "online";
    dirty = true;
  }

  if (now - lastAnim >= 500) {
    lastAnim = now;
    pulseFrame++;
    bootDots = (bootDots + 1) % 4;

    if (currentScreen == "boot" || currentScreen == "online") {
      dirty = true;
    }
  }

  if (currentScreen == "clock" && now - lastClockTick >= 1000) {
    lastClockTick = now;
    dirty = true;
  }

  if (alertUntil > 0 && now >= alertUntil && alertText.length() > 0) {
    alertText = "";
    alertUntil = 0;
    dirty = true;
  }

  if (dirty) {
    renderCurrent();
  }
}
