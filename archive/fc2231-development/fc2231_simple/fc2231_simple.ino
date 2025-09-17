/*
  FC2231 Force Sensor Monitor - Simple Version
  ===========================================
  
  Simplified Arduino sketch for FC2231 force sensor
  Compatible with kawaii Python interfaces
  
  Hardware Connections:
  - FC2231 VCC -> Arduino 5V
  - FC2231 GND -> Arduino GND  
  - FC2231 OUT -> Arduino A0
*/

// Simple configuration
const int SENSOR_PIN = A0;
const int READING_INTERVAL = 100;
const float REFERENCE_VOLTAGE = 5.0;
const int ADC_RESOLUTION = 1024;

// FC2231 specifications
const float SENSOR_MIN_VOLTAGE = 0.5;
const float SENSOR_MAX_VOLTAGE = 4.5;
const float MAX_FORCE_NEWTONS = 100.0;

// Variables
unsigned long readingCount = 0;
unsigned long lastReadingTime = 0;
float tare_voltage = 0.5;

void setup() {
  Serial.begin(9600);
  
  // Send startup messages
  Serial.println("FC2231,FORCE_SENSOR,STARTUP,OK");
  Serial.println("FC2231,READY,Kawaii_Force_Monitor,UwU");
  
  delay(1000);
}

void loop() {
  unsigned long currentTime = millis();
  
  // Take reading at specified interval
  if (currentTime - lastReadingTime >= READING_INTERVAL) {
    takeReading();
    lastReadingTime = currentTime;
  }
  
  // Check for commands
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    
    if (command == "TARE") {
      performTare();
    }
  }
}

void takeReading() {
  // Read sensor
  int rawADC = analogRead(SENSOR_PIN);
  float voltage = (rawADC * REFERENCE_VOLTAGE) / ADC_RESOLUTION;
  
  // Convert to force
  float adjustedVoltage = voltage;
  if (adjustedVoltage < SENSOR_MIN_VOLTAGE) adjustedVoltage = SENSOR_MIN_VOLTAGE;
  if (adjustedVoltage > SENSOR_MAX_VOLTAGE) adjustedVoltage = SENSOR_MAX_VOLTAGE;
  
  float voltageRange = SENSOR_MAX_VOLTAGE - SENSOR_MIN_VOLTAGE;
  float voltageRatio = (adjustedVoltage - tare_voltage) / voltageRange;
  float forceNewtons = voltageRatio * MAX_FORCE_NEWTONS;
  float forceGrams = forceNewtons * 101.97;
  
  // Ensure positive force
  if (forceNewtons < 0) forceNewtons = 0;
  if (forceGrams < 0) forceGrams = 0;
  
  readingCount++;
  
  // Send data: reading,voltage,V,temp,force_N,N,force_g,g,timestamp
  Serial.print(readingCount);
  Serial.print(",");
  Serial.print(voltage, 3);
  Serial.print(",V,");
  Serial.print("23.5");  // Fixed temperature
  Serial.print(",");
  Serial.print(forceNewtons, 3);
  Serial.print(",N,");
  Serial.print(forceGrams, 1);
  Serial.print(",g,");
  Serial.print(millis());
  Serial.println();
}

void performTare() {
  Serial.println("FC2231,TARE,STARTING,Taking_10_readings");
  
  float sum = 0;
  for (int i = 0; i < 10; i++) {
    int rawADC = analogRead(SENSOR_PIN);
    float voltage = (rawADC * REFERENCE_VOLTAGE) / ADC_RESOLUTION;
    sum += voltage;
    Serial.print("FC2231,TARE,READING,");
    Serial.print(i + 1);
    Serial.print("/10,");
    Serial.print(voltage, 4);
    Serial.println("V");
    delay(100);
  }
  
  tare_voltage = sum / 10.0;
  Serial.print("FC2231,TARE,COMPLETE,Voltage=");
  Serial.print(tare_voltage, 4);
  Serial.println("V");
}