# 🌸 Force Monitor ~ Kawaii Edition 🌸

*100% vibe coded with vscode copilot with model Claude Sonnet 4.0, without any shame, I won't apologize, when there ain't nowhere you can go, running away from pain when you've been victimized, tales from another broken home* 🌸

**Kawaii Arduino Force Sensor Monitoring System**

A professional-grade force monitoring system using FC2231 amplified force sensors with Arduino Uno R3, featuring a beautiful terminal interface with CSV data export capabilities.

## 👨‍🔬 Author Information

**Johnny Hamnesjö Olausson**  
📧 Email: johnny.hamnesjo@chalmers.se  
🏛️ Institution: Chalmers University of Technology  
📚 Department: Department of Industrial and Materials Science

## 📄 License

This project is licensed under the GNU General Public License v3.0.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

🌸 *Designed with kawaii simplicity and precision* 🌸

## What is this project?

This **Force Monitor** system interfaces with FC2231 amplified force sensors, a simple-to-use solution for measuring force and sending the data to your computer via serial (USB).

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Connect Hardware**
   - FC2231 sensor to Arduino Uno R3 analog pin A0
   - Arduino connected via USB (auto-detected on COM5)

3. **Run Terminal Monitor**
   ```bash
   python fc2231_terminal.py
   ```

## 🎮 Controls

- **'C'** - Calibrate sensor (tare to zero)
- **'E'** - Toggle CSV export recording  
- **'Q'** - Quit program gracefully
- **Ctrl+C** - Emergency stop

## 📊 Features

- ✅ **Real-time force monitoring** with 5-second display intervals
- ✅ **Professional CSV export** for data analysis
- ✅ **Persistent calibration** system with JSON storage
- ✅ **Temperature monitoring** from sensor
- ✅ **Kawaii terminal aesthetics** with status indicators
- ✅ **Session statistics** and data validation

## 📁 File Structure

### Active System
- `fc2231_terminal.py` - Main terminal interface
- `fc2231_calibration_manager.py` - Calibration system
- `fc2231_calibration.json` - Calibration data
- `FC2231_SYSTEM_GUIDE.md` - Detailed user guide
- `fc2231-datasheet.pdf` - Hardware specifications

### Archive
- `archive/openscale-system/` - Original OpenScale monitoring system
- `archive/fc2231-development/` - FC2231 development files and prototypes

## 📈 CSV Export Format

Exported files include:
- Reading sequence numbers
- Full timestamps with milliseconds  
- Voltage readings (V)
- Force measurements (N and g)
- Temperature data (°C)
- Status classifications

## 🔧 System Requirements

- Python 3.7+
- Windows with PowerShell
- Arduino Uno R3
- FC2231 Amplified Force Sensor
- USB cable for Arduino connection

## 🎌 Current Applications

### **🌸 Enhanced Terminal (Recommended)**
- `fc2231_terminal.py`: **Main terminal application** - Beautiful kawaii-inspired interface
  - Real-time force monitoring with cute aesthetics
  - Session statistics (min/max/average)
  - Precision calibration system
  - Data export to CSV
  - Kawaii-style interface with emojis

### **🔧 Archived Systems**
- `archive/openscale-system/`: **Original OpenScale system** - SparkFun OpenScale interface
- `archive/fc2231-development/`: **Development files** - Prototype GUIs and test scripts

## Usage

### Terminal Mode (Recommended)
```bash
python fc2231_terminal.py
```
- Press 'C' to calibrate (tare to zero)
- Press 'E' to toggle CSV export
- Press 'Q' to quit gracefully

## Load Cell Wiring

FC2231 Force Sensor → Arduino Uno R3:
- RED → 5V (Power)
- BLACK → GND (Ground)
- WHITE → A0 (Analog Signal)

## 📚 Documentation

See `FC2231_SYSTEM_GUIDE.md` for comprehensive setup and usage instructions.

## Useful Links

- [FC2231 Datasheet](fc2231-datasheet.pdf) - Local technical specifications
- [Arduino Uno R3 Reference](https://docs.arduino.cc/hardware/uno-rev3/)

---
*Designed with kawaii precision and love* 🌸