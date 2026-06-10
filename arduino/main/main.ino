#include <EEPROM.h>

const int pinLM35 = A0;
const int pinApa = A1;
const int pinLED = 8;

unsigned long timpPrecedent = 0;
const long intervalCitire = 2000;

const int pragInundatie = 500;

bool inundatieDetectata = false;
bool ledState = false;

// EEPROM
const int MAX_MESAJ = 20;
const int OFFSET_MESAJE = 20;

const int ADDR_INDEX_MESAJE = 10;
const int ADDR_INDEX_EVENIMENTE = 11;
const int ADDR_INIT_FLAG = 12;

int indexMesaje = 0;
int indexEvenimente = 0;


// =========================
// EEPROM
// =========================

void initEEPROM() {

  if (EEPROM.read(ADDR_INIT_FLAG) != 42) {

    Serial.println("Initializare EEPROM...");

    for (int i = 0; i < 220; i++) {
      EEPROM.update(i, 0);
    }

    EEPROM.update(ADDR_INDEX_MESAJE, 0);
    EEPROM.update(ADDR_INDEX_EVENIMENTE, 0);
    EEPROM.update(ADDR_INIT_FLAG, 42);

    Serial.println("EEPROM initializat.");
  }
}

void salveazaMesaj(String mesaj) {

  int adresa = OFFSET_MESAJE + (indexMesaje * MAX_MESAJ);

  for (int i = 0; i < MAX_MESAJ; i++) {

    if (i < mesaj.length()) {
      EEPROM.update(adresa + i, mesaj[i]);
    }
    else {
      EEPROM.update(adresa + i, 0);
    }
  }

  indexMesaje++;

  if (indexMesaje > 9)
    indexMesaje = 0;

  EEPROM.update(ADDR_INDEX_MESAJE, indexMesaje);

  Serial.println("Mesaj salvat.");
}

void afiseazaMesaje() {

  Serial.println("=== MESAJE EEPROM ===");

  bool gasit = false;

  for (int i = 0; i < 10; i++) {

    int slot = (indexMesaje + i) % 10;

    int adresa = OFFSET_MESAJE + (slot * MAX_MESAJ);

    String mesaj = "";

    for (int j = 0; j < MAX_MESAJ; j++) {

      char c = EEPROM.read(adresa + j);

      if (c == 0 || c == 255)
        break;

      mesaj += c;
    }

    if (mesaj.length() > 0) {

      Serial.print("#");
      Serial.print(i + 1);
      Serial.print(": ");

      Serial.println(mesaj);

      gasit = true;
    }
  }

  if (!gasit) {
    Serial.println("Niciun mesaj.");
  }

  Serial.println("=====================");
}


// =========================
// SETUP
// =========================

void setup() {

  Serial.begin(9600);

  pinMode(pinLED, OUTPUT);

  digitalWrite(pinLED, LOW);

  initEEPROM();

  indexMesaje = EEPROM.read(ADDR_INDEX_MESAJE);
  indexEvenimente = EEPROM.read(ADDR_INDEX_EVENIMENTE);

  Serial.println("Sistem pornit");
}


// =========================
// LOOP
// =========================

void loop() {

  unsigned long timpCurent = millis();

  // Afisare periodica in Serial Monitor

  if (timpCurent - timpPrecedent >= intervalCitire) {

    timpPrecedent = timpCurent;

    int rawTemp = analogRead(pinLM35);

    float voltage = rawTemp * (5.0 / 1023.0);

    float temperatura = voltage * 100.0;

    int valoareApa = analogRead(pinApa);

    Serial.print("Temp: ");
    Serial.print(temperatura);
    Serial.print(" C | Apa: ");
    Serial.println(valoareApa);

    if (valoareApa > pragInundatie && !inundatieDetectata) {

      inundatieDetectata = true;

      Serial.println("ALERTA: INUNDATIE!");

      EEPROM.update(indexEvenimente, 1);

      indexEvenimente++;

      if (indexEvenimente > 9)
        indexEvenimente = 0;

      EEPROM.update(ADDR_INDEX_EVENIMENTE, indexEvenimente);
    }

    else if (valoareApa < (pragInundatie - 50)) {

      inundatieDetectata = false;
    }
  }


  // Comenzi din Flask / Python

  if (Serial.available()) {

    String cmd = Serial.readStringUntil('\n');

    cmd.trim();

    // LED ON

    if (cmd == "A") {

      ledState = true;

      digitalWrite(pinLED, HIGH);
    }

    // LED OFF

    else if (cmd == "S") {

      ledState = false;

      digitalWrite(pinLED, LOW);
    }

    // TEMPERATURA

    else if (cmd == "T") {

      int raw = analogRead(pinLM35);

      float voltage = raw * (5.0 / 1023.0);

      float temperature = voltage * 100.0;

      Serial.println(temperature);
    }

    // STATUS LED

    else if (cmd == "L") {

      if (ledState)
        Serial.println("1");
      else
        Serial.println("0");
    }

    // STATUS INUNDATIE

    else if (cmd == "F") {

      int floodValue = analogRead(pinApa);

      if (floodValue > pragInundatie)
        Serial.println("1");
      else
        Serial.println("0");
    }

    // MESAJ DIN FLASK

    else if (cmd.startsWith("MSG:")) {

      String mesaj = cmd.substring(4);

      salveazaMesaj(mesaj);

      Serial.print("Mesaj primit: ");

      Serial.println(mesaj);
    }

    // AFISARE MESAJE EEPROM

    else if (cmd == "MESAJE") {

      afiseazaMesaje();
    }
  }
}