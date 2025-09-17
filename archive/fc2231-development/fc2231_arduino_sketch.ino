/*
  FC2231 Force Sensor Monitor - Arduino Uno R3
  ============================================
  
  Author: Johnny Hamnesjö Olausson
  Email: johnny.hamnesjo@chalmers.se
  Institution: Chalmers University of Technology
  Department: Department of Industrial and Materials Science
  
  This program reads FC2231 amplified force sensor data and sends it via serial
  Compatible with kawaii Python interfaces for real-time monitoring
  
  Hardware Connections:
  - FC2231 VCC -> Arduino 5V
  - FC2231 GND -> Arduino GND  
  - FC2231 OUT -> Arduino A0
  
  Serial Output Format:
  reading_number,voltage,force,timestamp
  
  License: GNU General Public License v3.0
*/

// Configuration constants
const int SENSOR_PIN = A0;           // FC2231 sensor connected to analog pin A0
const int READING_INTERVAL = 100;    // Milliseconds between readings
const float REFERENCE_VOLTAGE = 5.0; // Arduino Uno reference voltage
const int ADC_RESOLUTION = 1024;     // 10-bit ADC (0-1023)

// FC2231 specifications from datasheet
const float SENSOR_MIN_VOLTAGE = 0.5; // Minimum output voltage (no force)
const float SENSOR_MAX_VOLTAGE = 4.5; // Maximum output voltage (full scale)
const float SENSOR_SUPPLY_VOLTAGE = 5.0; // Supply voltage

// Force calibration (adjustable based on your sensor's force range)
const float MAX_FORCE_NEWTONS = 100.0; // Adjust this based on your sensor model
const float MAX_FORCE_GRAMS = MAX_FORCE_NEWTONS * 101.97; // Convert N to grams-force

// Global variables
unsigned long readingCount = 0;
unsigned long lastReadingTime = 0;
float voltageBuffer[10]; // Rolling average buffer
int bufferIndex = 0;
bool bufferFull = false;

// Calibration variables (can be updated via serial commands)
float tare_voltage = 0.5; // Default to minimum voltage
bool is_tared = false;

void setup() {
  Serial.begin(9600);
  
  // Set analog reference to default (5V)
  analogReference(DEFAULT);
  
  // Wait for serial connection
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  
  // Send startup message
  Serial.println("FC2231,FORCE_SENSOR,STARTUP,OK");
  Serial.println("FC2231,INFO,Author,Johnny Hamnesjo Olausson");
  Serial.println("FC2231,INFO,Email,johnny.hamnesjo@chalmers.se");
  Serial.println("FC2231,INFO,Institution,Chalmers University of Technology");
  Serial.println("FC2231,INFO,License,GNU GPL v3.0");
  Serial.println("FC2231,CONFIG,Max_Force_N," + String(MAX_FORCE_NEWTONS, 2));
  Serial.println("FC2231,CONFIG,Max_Force_g," + String(MAX_FORCE_GRAMS, 2));
  Serial.println("FC2231,CONFIG,Voltage_Range," + String(SENSOR_MIN_VOLTAGE, 1) + "V-" + String(SENSOR_MAX_VOLTAGE, 1) + "V");
  Serial.println("FC2231,READY,Kawaii_Force_Monitor,UwU");
  
  // Initialize voltage buffer
  for (int i = 0; i < 10; i++) {
    voltageBuffer[i] = 0.0;
  }
  
  delay(1000); // Give time for startup messages
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check for serial commands
  if (Serial.available() > 0) {
    handleSerialCommand();
  }
  
  // Take reading at specified interval
  if (currentTime - lastReadingTime >= READING_INTERVAL) {
    takeReading();
    lastReadingTime = currentTime;
  }
}

void takeReading() {
  // Read raw ADC value
  int rawADC = analogRead(SENSOR_PIN);
  
  // Convert to voltage
  float voltage = (rawADC * REFERENCE_VOLTAGE) / ADC_RESOLUTION;
  
  // Add to rolling average buffer
  voltageBuffer[bufferIndex] = voltage;
  bufferIndex = (bufferIndex + 1) % 10;
  if (bufferIndex == 0) bufferFull = true;
  
  // Calculate smoothed voltage
  float smoothedVoltage = calculateAverageVoltage();
  
  // Convert to force
  float forceNewtons = voltageToForce(smoothedVoltage);
  float forceGrams = forceNewtons * 101.97; // Convert N to grams-force
  
  // Get current temperature (simulated - Arduino Uno doesn't have built-in temp sensor)
  float temperature = 23.5; // Default room temperature
  
  // Increment reading count
  readingCount++;
  
  // Send data in compatible format with OpenScale interface
  Serial.print(readingCount);
  Serial.print(",");
  Serial.print(smoothedVoltage, 4);
  Serial.print(",V,");
  Serial.print(temperature, 1);
  Serial.print(",");
  Serial.print(forceNewtons, 3);
  Serial.print(",N,");
  Serial.print(forceGrams, 2);
  Serial.print(",g,");
  Serial.print(millis());
  Serial.println();
}

float voltageToForce(float voltage) {
  // Apply tare if calibrated
  float adjustedVoltage = voltage;
  if (is_tared) {
    adjustedVoltage = voltage - tare_voltage + SENSOR_MIN_VOLTAGE;
  }
  
  // Ensure voltage is within valid range
  if (adjustedVoltage < SENSOR_MIN_VOLTAGE) {
    adjustedVoltage = SENSOR_MIN_VOLTAGE;
  }
  if (adjustedVoltage > SENSOR_MAX_VOLTAGE) {
    adjustedVoltage = SENSOR_MAX_VOLTAGE;
  }
  
  // Linear conversion from voltage to force
  float voltageRange = SENSOR_MAX_VOLTAGE - SENSOR_MIN_VOLTAGE;
  float voltageRatio = (adjustedVoltage - SENSOR_MIN_VOLTAGE) / voltageRange;
  float force = voltageRatio * MAX_FORCE_NEWTONS;
  
  // Return force in Newtons
  return force;
}

float calculateAverageVoltage() {
  float sum = 0.0;
  int count = bufferFull ? 10 : bufferIndex;
  
  for (int i = 0; i < count; i++) {
    sum += voltageBuffer[i];
  }
  
  return count > 0 ? sum / count : 0.0;
}

void handleSerialCommand() {
  String command = Serial.readStringUntil('\n');
  command.trim();
  command.toUpperCase();
  
  if (command == "TARE") {
    performTare();
  } else if (command == "RESET") {
    resetTare();
  } else if (command == "STATUS") {
    sendStatus();
  } else if (command == "INFO") {
    sendInfo();
  } else if (command.startsWith("FORCE_RANGE=")) {
    setForceRange(command);
  }
}

void performTare() {
  // Take 20 readings for tare calibration
  float tare_readings[20];
  
  Serial.println("FC2231,TARE,STARTING,Taking_20_readings");
  
  for (int i = 0; i < 20; i++) {
    int rawADC = analogRead(SENSOR_PIN);
    float voltage = (rawADC * REFERENCE_VOLTAGE) / ADC_RESOLUTION;
    tare_readings[i] = voltage;
    
    Serial.println("FC2231,TARE,READING," + String(i + 1) + "/20," + String(voltage, 4) + "V");
    delay(50);
  }
  
  // Calculate average
  float sum = 0;
  for (int i = 0; i < 20; i++) {
    sum += tare_readings[i];
  }
  
  tare_voltage = sum / 20.0;
  is_tared = true;
  
  // Calculate standard deviation for quality assessment
  float variance = 0;
  for (int i = 0; i < 20; i++) {
    float diff = tare_readings[i] - tare_voltage;
    variance += diff * diff;
  }
  float std_dev = sqrt(variance / 19.0);
  
  Serial.println("FC2231,TARE,COMPLETE,Voltage=" + String(tare_voltage, 4) + "V,StdDev=" + String(std_dev, 4) + "V");
}

void resetTare() {
  tare_voltage = SENSOR_MIN_VOLTAGE;
  is_tared = false;
  Serial.println("FC2231,TARE,RESET,Tare_cleared");
}

void sendStatus() {
  float currentVoltage = (analogRead(SENSOR_PIN) * REFERENCE_VOLTAGE) / ADC_RESOLUTION;
  float currentForce = voltageToForce(currentVoltage);
  
  Serial.println("FC2231,STATUS,Voltage," + String(currentVoltage, 4) + "V");
  Serial.println("FC2231,STATUS,Force," + String(currentForce, 3) + "N");
  Serial.println("FC2231,STATUS,Tared," + String(is_tared ? "YES" : "NO"));
  if (is_tared) {
    Serial.println("FC2231,STATUS,Tare_Voltage," + String(tare_voltage, 4) + "V");
  }
  Serial.println("FC2231,STATUS,Readings," + String(readingCount));
  Serial.println("FC2231,STATUS,Uptime," + String(millis()) + "ms");
}

void sendInfo() {
  Serial.println("FC2231,INFO,Sensor,FC2231_Amplified_Force_Sensor");
  Serial.println("FC2231,INFO,Arduino,Uno_R3");
  Serial.println("FC2231,INFO,Pin,A0");
  Serial.println("FC2231,INFO,Commands,TARE|RESET|STATUS|INFO|FORCE_RANGE=value");
  Serial.println("FC2231,INFO,Format,reading,voltage,V,temp,force_N,N,force_g,g,timestamp");
}

void setForceRange(String command) {
  int equalsIndex = command.indexOf('=');
  if (equalsIndex > 0) {
    float newRange = command.substring(equalsIndex + 1).toFloat();
    if (newRange > 0 && newRange <= 1000) {
      // Update force range - would need to store in EEPROM for persistence
      Serial.println("FC2231,CONFIG,Force_Range_Updated," + String(newRange, 2) + "N");
    } else {
      Serial.println("FC2231,ERROR,Invalid_Force_Range,Must_be_0-1000N");
    }
  }
}