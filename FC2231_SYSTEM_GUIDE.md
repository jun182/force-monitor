# 🌸 FC2231 Force Monitor System 🌸

## Overview

Complete Arduino-based force monitoring system for FC2231 amplified force sensors with kawaii Python interfaces, persistent calibration, and real-time data visualization.

## 🔌 Hardware Setup

### Required Components:
- **Arduino Uno R3**
- **FC2231 Amplified Force Sensor** 
- **USB Cable** (Arduino to PC)
- **Jumper Wires**

### Wiring Connections:
```
FC2231 Sensor    →    Arduino Uno R3
─────────────────────────────────────
VCC (Red)        →    5V
GND (Black)      →    GND  
OUT (Yellow)     →    A0 (Analog Pin 0)
```

### FC2231 Specifications:
- **Output Voltage Range**: 0.5V - 4.5V
- **Supply Voltage**: 5V DC
- **Output Type**: Analog voltage proportional to force
- **Response**: Linear (from datasheet)

## 📁 Files Created

### Arduino Code:
- **`fc2231_arduino_sketch.ino`** - Arduino sketch for sensor reading

### Python Programs:
- **`fc2231_calibration_manager.py`** - Persistent calibration system
- **`fc2231_terminal.py`** - Kawaii terminal interface
- **`fc2231_gui.py`** - Kawaii GUI with real-time plotting

## 🚀 Quick Start Guide

### Step 1: Upload Arduino Code
1. Open `fc2231_arduino_sketch.ino` in Arduino IDE
2. Connect Arduino Uno R3 via USB
3. Select correct board and port
4. Upload the sketch

### Step 2: Wire the Sensor
1. Connect FC2231 according to wiring diagram above
2. Ensure secure connections
3. Power Arduino via USB

### Step 3: Run Python Interface

**Terminal Interface:**
```bash
python fc2231_terminal.py
```

**GUI Interface:**
```bash
python fc2231_gui.py
```

## 🎛️ Using the System

### Terminal Interface (`fc2231_terminal.py`)

**Features:**
- Real-time force monitoring in kawaii style
- Voltage and force readings (N and g)
- Session statistics
- Live calibration with 'c' key
- Compatible output format

**Controls:**
- **Ctrl+C**: Stop monitoring
- **'c' key**: Start calibration process
- **Arduino commands**: TARE, STATUS, INFO, RESET

**Sample Output:**
```
Reading# | Voltage | Status     | Force(N) | Force(g) | Temp  | Time
----------------------------------------------------------------------
     1 |  0.523V | 🌸 ZERO    |   0.00N |     0.0g |  23.5° | 14:32:15
     2 |  2.156V | 💪 MEDIUM  |  41.40N |  4223.5g |  23.5° | 14:32:16
```

### GUI Interface (`fc2231_gui.py`)

**Features:**
- Real-time voltage and force display
- Live plotting of both voltage and force
- Session statistics with min/max/average
- Calibration buttons (Quick Tare & Full Calibration)
- Data export to CSV
- Professional kawaii design

**Controls:**
- **🟢 Start Reading**: Connect to Arduino and begin monitoring
- **🔴 Stop Reading**: Disconnect and stop monitoring
- **🎯 Quick Tare**: Set current reading as zero point
- **⚖️ Calibrate Zero**: 20-point statistical calibration
- **💾 Export Data**: Save session data to CSV

## ⚖️ Calibration System

### Persistent Calibration
- Calibration saved to `fc2231_calibration.json`
- Automatic loading on startup
- Backup system for safety
- Validation and error checking

### Calibration Types

**1. Quick Tare (Instant Zero):**
- Uses current reading as new zero point
- Instant application
- Good for quick adjustments

**2. Full Calibration (20-point Statistical):**
- Takes 20 readings for accuracy
- Calculates mean and standard deviation
- Provides stability assessment
- Recommended for best accuracy

### Calibration Data Structure:
```json
{
    "tare_voltage": 0.523,
    "max_force_newtons": 100.0,
    "voltage_min": 0.5,
    "voltage_max": 4.5,
    "calibration_date": "2025-09-16T16:30:22.123456",
    "calibration_stability": 0.002,
    "serial_port": "COM3",
    "arduino_board": "Uno R3",
    "sensor_model": "FC2231",
    "version": "1.0"
}
```

## 🔧 Arduino Commands

Send via Serial Monitor or Python:

- **`TARE`** - Perform 20-point tare calibration
- **`RESET`** - Reset tare to default
- **`STATUS`** - Get current sensor status
- **`INFO`** - Get system information
- **`FORCE_RANGE=value`** - Set maximum force range

## 📊 Data Format

### Arduino Serial Output:
```
reading_number,voltage,V,temperature,force_N,N,force_g,g,timestamp
1,0.523,V,23.5,0.575,N,58.6,g,1000
```

### CSV Export Format:
```csv
Timestamp,Voltage (V),Force (N),Force (g)
2025-09-16 14:32:15.123,0.523,0.575,58.6
```

## 🎯 Force Conversion

### Voltage to Force Formula:
```python
# Apply tare
adjusted_voltage = voltage - tare_voltage + voltage_min

# Linear conversion
voltage_range = voltage_max - voltage_min  # 4.0V
voltage_ratio = (adjusted_voltage - voltage_min) / voltage_range
force_newtons = voltage_ratio * max_force_newtons

# Convert to grams-force
force_grams = force_newtons * 101.97
```

### Default Ranges:
- **Voltage Range**: 0.5V - 4.5V (4.0V span)
- **Force Range**: 0N - 100N (adjustable)
- **Conversion**: 1N = 101.97 grams-force

## 🔍 Troubleshooting

### Common Issues:

**"Serial connection error"**
- Check Arduino USB connection
- Verify correct COM port (usually COM3-COM8)
- Ensure Arduino sketch is uploaded
- Try different USB cable

**"No readings appearing"**
- Check sensor wiring (VCC, GND, OUT)
- Verify 5V power supply to sensor
- Ensure analog pin A0 connection
- Check for loose connections

**"Readings seem wrong"**
- Perform fresh calibration
- Check if force range is appropriate
- Verify sensor is properly mounted
- Ensure no mechanical interference

**"Python module errors"**
- Install required modules: `pip install pyserial matplotlib tkinter`
- Check Python version (3.6+)
- Verify file paths and permissions

### Arduino Serial Monitor Test:
1. Open Arduino IDE Serial Monitor
2. Set baud rate to 9600
3. Should see startup messages and data streams
4. Try commands like `STATUS` or `INFO`

## 🌟 Advanced Features

### Multiple Sensors
The Arduino code is designed to be easily expandable:
- Change `SENSOR_PIN` for different analog pins
- Add arrays for multiple sensors
- Modify output format for sensor identification

### Custom Force Ranges
Adjust maximum force based on your sensor model:
```cpp
const float MAX_FORCE_NEWTONS = 50.0;  // For lighter sensors
const float MAX_FORCE_NEWTONS = 500.0; // For heavier sensors
```

### Data Logging
- CSV export includes full metadata
- Timestamps with millisecond precision
- Session statistics and calibration info
- Compatible with Excel and scientific software

## 📈 Performance

### Specifications:
- **Sampling Rate**: ~10 Hz (adjustable)
- **Resolution**: 10-bit ADC (1024 levels)
- **Voltage Resolution**: ~4.9mV per step
- **Force Resolution**: Depends on force range setting
- **Stability**: Typically ±0.001V with good connections

### Accuracy Notes:
- Arduino ADC accuracy: ±2 LSB typical
- Reference voltage stability affects accuracy
- Temperature effects minimal for short sessions
- Mechanical mounting affects noise levels

## 🎨 Customization

### Colors and Styling:
Both Python interfaces use kawaii color schemes that can be customized in the source code.

### Output Formats:
Easy to modify for different data formats or integration with other systems.

### Force Units:
Currently supports Newtons and grams-force, easily expandable for other units.

---

## 🌸 Kawaii Engineering Excellence 🌸

**Author:** Johnny Hamnesjö Olausson  
**Email:** johnny.hamnesjo@chalmers.se  
**Institution:** Chalmers University of Technology  
**Department:** Department of Industrial and Materials Science  

*Designed with precision, built with love, presented with kawaii aesthetics! UwU*

---

## 📄 License

GNU General Public License v3.0 - Feel free to use, modify, and share!