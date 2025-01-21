#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <ESP8266WiFi.h>                               
#include <ESP8266HTTPClient.h>
#include <Servo.h>

////////////////// Pinbelegung ///////////////////////////////////////////////////////////////////////////////
#define TRIGPIN                         14              // Ultraschallsensor (Trig)
#define ECHOPIN                         12              // Ultraschallsensor (Echo)
#define WATERPUMPPIN                    0               // Wasserpumpe
#define YL69PIN                         A0              // Bodenfeuchtigkeitssensor
#define SBXPIN                          16              // Lichtsensor
#define DHTPIN                          2               // Temperatur, Luftfeuchtigkeit und Luftdruck
#define SG90PIN                         13              // Servo-Motor

////////////////// Konfiguration /////////////////////////////////////////////////////////////////////////////
// Allgemeines
#define BAUDRATE                        9600            // Baudrate des Arduinos
#define DHTTYPE                         DHT22           // DHT22

// LCD-Display
#define LCDADDRESS                      0x27            // Adresse des LCD-Displays
#define LCDROWS                         4               // Anzahl der Zeilen des LCD-Displays
#define LCDCOULUMNS                     20              // Anzahl der Spalten des LCD-Displays

// Wassertank
const float waterDistanceEmpty      =   30.0;           // Distanz des Wassers bei leerem Tank
const float waterDistanceFull       =   10.0;           // Distanz des Wassers bei vollem Tank

// Bodenfeuchtigkeit
const float soilHumidityOptimal     =   30.0;           // Optimale Bodenfeuchtigkeit
const float soilHumidityThreshold   =   5.0;            // PROZENTUALER Schwellwert für Bodenfeuchtigkeit

// Licht
const int maxSunlightDuration       =   5;              // Dauer der Lichteinstrahlung, bis Servo weiter dreht

// WiFi
const char* ssid     = "YOUR SSID";                     // SSID (Name) der Wi-Fi network
const char* password = "YOUR PASSWORD";                 // Password der Wi-Fi network
const char* url      = "http://localhost:5000/pushdata?";  // URL zum Server

////////////////// Objektdefinitionen /////////////////////////////////////////////////////////////////////////
LiquidCrystal_I2C lcd(LCDADDRESS, LCDCOULUMNS, LCDROWS);        // LCD-Display
DHT dht(DHTPIN, DHTTYPE);
Servo servo;

////////////////// Variablen /////////////////////////////////////////////////////////////////////////////////
// Relais
bool waterPumpActive                  = false;

// Wassertank
long  waterContainerDistanceReal;                       // Aktuelle Distanz Wasser <--> Sensor (tatsächlich gemessen)
long  waterContainerDistance;                           // Aktuelle Distanz Wasser <--> Sensor (zwischen min und max geclaimed)
float waterContainerPercentage;                         // Aktueller Füllstand des Wassertanks

// Bodenfeuchtigkeit                           
float soilHumidityPercentage;                           // Aktuelle Bodenfeuchtigkeit

// Luftfeuchtigkeit
float humidityPercentage;                               // Aktuelle Luftfeuchtigkeit

// Temperatur
float temperature;                                      // Aktuelle Temperatur

//Lichteinstrahlung
float lightIntensity;                                   // Aktuelle Lichteinstrahlung
int sunlightDuration                  = 0;              // Sekunden mit Lichteinstrahlung, seit letzer Drehung
int servoDegree                       = 0;              // Aktuelle Rotation
int servoSteps                        = 10;              // Schritte, die der Servo Rotieren soll (Grad)

////////////////// Programmierung ////////////////////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(BAUDRATE);

  Serial.println("Setup pins");
  // Modi der Pins setzen
  pinMode(TRIGPIN, OUTPUT);                             // Ultraschallsensor (Trig)
  pinMode(ECHOPIN, INPUT);                              // Ultraschallsensor (Echo)
  pinMode(WATERPUMPPIN, OUTPUT);                        // Wasserpumpe

  Serial.println("Initialise objects");
  // Objekte initialisieren

  Wire.begin();

  // LCD Display
  //lcd.begin();
  lcd.init();
  lcd.backlight();

  // Luftfeuchtigkeit + Temperatur + Druck
  dht.begin();  

  // Wasserpumpe zu beginn deaktivieren
  digitalWrite(WATERPUMPPIN, HIGH);

  // Servo initialisieren
  servo.attach(SG90PIN);
  servo.write(0);

  Serial.println("Connect wifi");
  connectWiFi();

}

void loop() {

  delay(500);
  setServoPosition(servoDegree);
  delay(500);

  // Daten aktualisieren
  updateData();

  // Daten an Server senden
  sendData();

  // Sensoren steuern
  controlComplete();

  // Daten visualisieren
  Serial.print("Wasserfüllstand: ");
  Serial.print(waterContainerPercentage);
  Serial.print("% (Distanz: ");
  Serial.print(waterContainerDistance);
  Serial.print(" cm (claimed) - ");
  Serial.print(waterContainerDistanceReal);
  Serial.println(" cm (real))");

  Serial.print("Bodenfeuchtigkeit: ");
  Serial.print(soilHumidityPercentage);
  Serial.print("%");
  Serial.print(" (Optimal: ");
  Serial.print(soilHumidityOptimal);
  Serial.print("% - Threshold: ");
  Serial.print((soilHumidityOptimal - (soilHumidityOptimal * soilHumidityThreshold / 100)));
  Serial.println("%)");

  Serial.print("Luftfeuchtigkeit: ");
  Serial.print(humidityPercentage);
  Serial.println("%");

  Serial.print("Temperatur: ");
  Serial.print(temperature);
  Serial.println("C");

  Serial.print("Lichtsensor: ");
  Serial.print(lightIntensity);
  Serial.println("lux");
}

void controlComplete() {
  controlWaterPump();
  controlDisplay();
}

// Wasserpumpe an- und ausschalten
void controlWaterPump() {  
  if(waterContainerPercentage < 5.0) {                                                                          // Bei einem Füllstand des Wassertanks von weniger als 5% abbrechen, da zu wenig Wasser vorhanden
    writeWaterPump(false);                                                                                      // Wasserpumpe ausschalten
  } 
  else if(waterPumpActive) {   
    if(soilHumidityPercentage > soilHumidityOptimal) {                                                          // Wenn die Bodenfeuchtigkeit die Optimalbodenfeuchtigkeit erreicht hat
      writeWaterPump(false);                                                                                    // Wasserpumpe anschalten
    } 
  } else {  
    if(soilHumidityPercentage < (soilHumidityOptimal - (soilHumidityOptimal * soilHumidityThreshold / 100))) {  // Wenn die Bodenfeuchtigkeit um [soilHumidityThreshold]% unter der Optimalbodenfeuchtigkeit liegt
      writeWaterPump(true);                                                                                     // Wasserpumpe ausschalten
    } 
  }
}

// Display steuern
void controlDisplay() {
  lcd.clear();

  // Wasserfüllstand anzeigen
  lcd.setCursor (0, 1);
  lcd.print("Wasser    ");
  for(int i = 0; i < round(waterContainerPercentage * 0.1); i++)
  {
    lcd.print("#");
  }

  // Temperatur anzeigen
  lcd.setCursor (0, 2);
  lcd.print("T:");
  lcd.print(temperature,1);
  lcd.print("C  ");
  lcd.print("Sonne: ");
  lcd.print(sunlightDuration);


  // Feuchtigkeiten anzeigen
  lcd.setCursor (0, 3);
  lcd.print("Luft ");
  lcd.print(humidityPercentage, 1);
  lcd.print(" Erde ");
  lcd.print(soilHumidityPercentage, 1);
}

void updateData() {
  Serial.println("Update data");
  readWaterContainer();
  readSoilHumidity();
  readHumidityAndTemperature();
  readLightIntensity();
}

// Aktualisierung des Wassertankfüllstandes
void readWaterContainer() {
  Serial.println("Read water container");
  digitalWrite(TRIGPIN, LOW);
  delayMicroseconds(5);
  digitalWrite(TRIGPIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGPIN, LOW);
  
  pinMode(ECHOPIN, INPUT);
  long duration = pulseIn(ECHOPIN, HIGH);
  waterContainerDistanceReal = (duration / 2) / 29.1;

  // Zwischen waterDistanceFull und waterDistanceEmpty claimen
  if(waterContainerDistanceReal < waterDistanceFull) { waterContainerDistance = waterDistanceFull; }
  else if(waterContainerDistanceReal > waterDistanceEmpty) { waterContainerDistance = waterDistanceEmpty; }
  else { waterContainerDistance = waterContainerDistanceReal; }
  
  waterContainerPercentage = (waterContainerDistance - waterDistanceFull) / (waterDistanceEmpty - waterDistanceFull) * 100;
}

// Aktualisierung der Bodenfeuchtigkeit
void readSoilHumidity() {
  Serial.println("Read soil humidity");

  int shSum = 0;
  for(int i = 0; i < 16; i++) {
    shSum += analogRead(YL69PIN);
  }

  float avgSoilHumidity = shSum /16;
  Serial.println(avgSoilHumidity);
  soilHumidityPercentage = map(avgSoilHumidity, 1023, 300, 0, 100);
}

// Aktualisierung der Luftfeuchtigkeit und Temperatur
void readHumidityAndTemperature() {
  Serial.println("Read humidity and temperature");

  float hSum = 0;
  float tSum = 0;
  for(int i = 0; i < 16; i++) {
    hSum += dht.readHumidity();
    tSum += dht.readTemperature();
  }

  humidityPercentage = hSum / 16;
  temperature = tSum / 16;
}

//Lichtintensitaet messen
void readLightIntensity() {
  Serial.println("Read light intesity");
  int luxValue = digitalRead(SBXPIN);
  lightIntensity = luxValue;

  if(luxValue < 1) {
    sunlightDuration += 1;
    if(sunlightDuration >= maxSunlightDuration) {
      sunlightDuration = 0;
      servoDegree += servoSteps;

      if(servoDegree > 180 || servoDegree < 0) {
        servoSteps *= -1;
        servoDegree += 2 * servoSteps;
      }
    }
  }
}

// An- und ausschalten der Wasserpumpe
void writeWaterPump(bool active) {
  if (waterPumpActive == active) return;
  
  if (active) { digitalWrite(WATERPUMPPIN, HIGH); } 
  else { digitalWrite(WATERPUMPPIN, LOW); }
  waterPumpActive = active;
}

void sendData()
{
  if(WiFi.status() != WL_CONNECTED){                           
    connectWiFi();
  }

  char sendChars[128];
  strcpy_P(sendChars, url);

  // Teparatur
  strcat_P(sendChars, PSTR("t="));
  dtostrf(temperature, 4, 2, &sendChars[strlen(sendChars)]);

  //Distanz Sensor <---> Wasseroberfläche
  strcat_P(sendChars, PSTR("&wc="));
  dtostrf(waterContainerPercentage, 4, 2, &sendChars[strlen(sendChars)]);

  // Bodenfeuchtigkeit
  strcat_P(sendChars, PSTR("&sh="));
  dtostrf(soilHumidityPercentage, 4, 2, &sendChars[strlen(sendChars)]);

  // Luftfeuchtigkeit
  strcat_P(sendChars, PSTR("&ah="));
  dtostrf(humidityPercentage, 4, 2, &sendChars[strlen(sendChars)]);

  // Lichteinstrahlung
  strcat_P(sendChars, PSTR("&l="));
  dtostrf(lightIntensity, 4, 2, &sendChars[strlen(sendChars)]);

  // Lichteinstrahlung
  strcat_P(sendChars, PSTR("&isw="));
  dtostrf(waterPumpActive, 4, 2, &sendChars[strlen(sendChars)]);

  // Lichteinstrahlung
  strcat_P(sendChars, PSTR("&rot="));
  dtostrf(servoDegree, 4, 2, &sendChars[strlen(sendChars)]);

  // Lichteinstrahlung
  strcat_P(sendChars, PSTR("&sl="));
  dtostrf(sunlightDuration, 4, 2, &sendChars[strlen(sendChars)]);

  HTTPClient http;   
  http.begin(sendChars);  

  int httpCode = http.GET();                                
  if (httpCode > 0) {                                       
    String payload = http.getString();                      
    Serial.println(payload);                                
  }

  http.end();                                              
}

void connectWiFi() {
  WiFi.begin(ssid, password);                                 
  Serial.print("Connecting to ");
  Serial.print(ssid); Serial.println(" ...");
  
  lcd.clear();
  lcd.setCursor (0, 0);
  lcd.print("Connecting to ");
  lcd.print(ssid);

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) {                     
    delay(1000);
    Serial.println(++i);

    lcd.setCursor (0, 3);
    lcd.print(i);

    if(i % 30 == 0) {
      WiFi.begin(ssid, password);
      lcd.print(" retry");
    }
  }

  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP()); 
}

void setServoPosition(int degree) {
  servo.write(degree);
}
