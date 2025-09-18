# 🌸 Force Monitor ~ Kawaii Edition 🌸

# FC2231 Force Monitor - Terminal Interface# 🌸 Force Monitor ~ Kawaii Edition 🌸

*100% vibe coded with vscode copilot with model Claude Sonnet 4.0, without any shame, I won't apologize, when there ain't nowhere you can go, running away from pain when you've been victimized, tales from another broken home* 🌸=======

100% vibe coded with vscode copilot with model Claude Sonnet 4.0, without any shame, I won't apologize, when there ain't nowhere you can go,

**Kawaii Arduino Force Sensor Monitoring System**

running away from pain when you've been victimized, tales from another broken,

A professional-grade force monitoring system using FC2231 amplified force sensors with Arduino Uno R3, featuring a beautiful terminal interface with CSV data export capabilities.

home

## 👨‍🔬 Author Information

# 🌸 Force Monitor ~ Kawaii Edition 🌸

**Johnny Hamnesjö Olausson**

📧 Email: johnny.hamnesjo@chalmers.se  

🏛️ Institution: Chalmers University of Technology  

📚 Department: Department of Industrial and Materials Science

🌸 **Kawaii Arduino Force Sensor Monitoring System** 🌸**Precision Weight Measurement Interface**

## 📄 License



This project is licensed under the GNU General Public License v3.0.

A professional-grade force monitoring system using FC2231 amplified force sensors with Arduino Uno R3, featuring a beautiful terminal interface with CSV data export capabilities.## 👨‍🔬 Author Information

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.



🌸 *Designed with kawaii simplicity and precision* 🌸

## 🚀 Quick Start**Johnny Hamnesjö Olausson**  

## What is this project?

📧 Email: johnny.hamnesjo@chalmers.se  

This **Force Monitor** system interfaces with FC2231 amplified force sensors, a simple-to-use solution for measuring force and sending the data to your computer via serial (USB).

1. **Install Dependencies**🏛️ Institution: Chalmers University of Technology  

## 🚀 Quick Start

   ```bash📚 Department: Department of Industrial and Materials Science

1. **Install Dependencies**

   ```bash   pip install -r requirements.txt

   pip install -r requirements.txt

   ```   ```## 📄 License



2. **Connect Hardware**

   - FC2231 sensor to Arduino Uno R3 analog pin A0

   - Arduino connected via USB (auto-detected on COM5)2. **Connect Hardware**This project is licensed under the GNU General Public License v3.0.



3. **Run Terminal Monitor**   - FC2231 sensor to Arduino Uno R3 analog pin A0

   ```bash

   python fc2231_terminal.py   - Arduino connected via USB (auto-detected on COM5)This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

   ```



## 🎮 Controls

3. **Run Terminal Monitor**🌸 *Designed with kawaii simplicity and precision* 🌸

- **'C'** - Calibrate sensor (tare to zero)

- **'E'** - Toggle CSV export recording     ```bash

- **'Q'** - Quit program gracefully

- **Ctrl+C** - Emergency stop   python fc2231_terminal.py## What is this project?



## 📊 Features   ```This **Force Monitor** system interfaces with SparkFun OpenScale, a simple-to-use open source solution for measuring load cells and sending the data to your computer via serial (USB).



- ✅ **Real-time force monitoring** with 5-second display intervals

- ✅ **Professional CSV export** for data analysis

- ✅ **Persistent calibration** system with JSON storage## 🎮 Controls## Getting Started

- ✅ **Temperature monitoring** from sensor

- ✅ **Kawaii terminal aesthetics** with status indicators1. Connect your OpenScale to your PC via USB (should appear on COM4)

- ✅ **Session statistics** and data validation

- **'C'** - Calibrate sensor (tare to zero)2. Install Python 3.x from https://www.python.org/

## 📁 File Structure

- **'E'** - Toggle CSV export recording  3. Install dependencies: `pip install -r requirements.txt`

### Active System

- `fc2231_terminal.py` - Main terminal interface- **'Q'** - Quit program gracefully4. Mount your load cell properly (clamp one end, load the other end)

- `fc2231_calibration_manager.py` - Calibration system

- `fc2231_calibration.json` - Calibration data- **Ctrl+C** - Emergency stop5. Run the enhanced GUI: `python enhanced_gui.py`

- `FC2231_SYSTEM_GUIDE.md` - Detailed user guide

- `fc2231-datasheet.pdf` - Hardware specifications



### Archive## 📊 Features## 🎌 Current Applications

- `archive/openscale-system/` - Original OpenScale monitoring system

- `archive/fc2231-development/` - FC2231 development files and prototypes



## 📈 CSV Export Format- ✅ **Real-time force monitoring** with 5-second display intervals### **🌸 Enhanced GUI (Recommended)**



Exported files include:- ✅ **Professional CSV export** for data analysis- `enhanced_gui.py`: **Main GUI application** - Beautiful kawaii-inspired interface

- Reading sequence numbers

- Full timestamps with milliseconds  - ✅ **Persistent calibration** system with JSON storage  - Real-time weight monitoring with cute aesthetics

- Voltage readings (V)

- Force measurements (N and g)- ✅ **Temperature monitoring** from sensor  - Session statistics (min/max/average)

- Temperature data (°C)

- Status classifications- ✅ **Kawaii terminal aesthetics** with status indicators  - Precision calibration system



## 🔧 System Requirements- ✅ **Session statistics** and data validation  - Data export to CSV



- Python 3.7+  - Kawaii-style interface with emojis

- Windows with PowerShell

- Arduino Uno R3## 📁 File Structure

- FC2231 Amplified Force Sensor

- USB cable for Arduino connection### **⛩️ Kawaii Terminal**



## 🎌 Current Applications### Active System- `zen_terminal.py`: **Beautiful terminal interface** - Command line with kawaii styling



### **🌸 Enhanced Terminal (Recommended)**- `fc2231_terminal.py` - Main terminal interface  - Elegant display with emojis

- `fc2231_terminal.py`: **Main terminal application** - Beautiful kawaii-inspired interface

  - Real-time force monitoring with cute aesthetics- `fc2231_calibration_manager.py` - Calibration system  - Session statistics

  - Session statistics (min/max/average)

  - Precision calibration system- `fc2231_calibration.json` - Calibration data  - UwU-style status messages

  - Data export to CSV

  - Kawaii-style interface with emojis- `FC2231_SYSTEM_GUIDE.md` - Detailed user guide



### **🔧 Archived Systems**- `fc2231-datasheet.pdf` - Hardware specifications### **🔧 Utility Tools**

- `archive/openscale-system/`: **Original OpenScale system** - SparkFun OpenScale interface

- `archive/fc2231-development/`: **Development files** - Prototype GUIs and test scripts- `openscale_gui.py`: **Original GUI** - Basic visual interface



## Usage### Archive- `tared_scale.py`: **Terminal interface** - Command line monitoring



### Terminal Mode (Recommended)- `archive/openscale-system/` - Original OpenScale monitoring system- `tare_scale.py`: **Calibration tool** - Set new zero point

```bash

python fc2231_terminal.py- `archive/fc2231-development/` - FC2231 development files and prototypes- `accurate_scale_monitor.py`: **Advanced terminal** - High precision monitoring

```

- Press 'C' to calibrate (tare to zero)- `drift_monitor.py`: **Diagnostic tool** - Monitor stability over time

- Press 'E' to toggle CSV export

- Press 'Q' to quit gracefully## 📈 CSV Export Format- `requirements.txt`: Python dependencies



## Load Cell Wiring- `calibration_data.txt`: Stored calibration parameters



FC2231 Force Sensor → Arduino Uno R3:Exported files include:- `drift_data.csv`: Drift analysis data

- RED → 5V (Power)

- BLACK → GND (Ground)- Reading sequence numbers

- WHITE → A0 (Analog Signal)

- Full timestamps with milliseconds  ## Usage

## 📚 Documentation

- Voltage readings (V)### GUI Mode (Recommended)

See `FC2231_SYSTEM_GUIDE.md` for comprehensive setup and usage instructions.

- Force measurements (N and g)```bash

## Useful Links

- Temperature data (°C)python openscale_gui.py

- [FC2231 Datasheet](fc2231-datasheet.pdf) - Local technical specifications

- [Arduino Uno R3 Reference](https://docs.arduino.cc/hardware/uno-rev3/)- Status classifications```



---- Click "Start" to begin monitoring

*Designed with kawaii precision and love* 🌸
## 🔧 System Requirements- Click "Tare (Zero)" to reset zero point

- Place objects on load cell to measure weight

- Python 3.7+

- Windows with PowerShell### Terminal Mode

- Arduino Uno R3```bash

- FC2231 Amplified Force Sensorpython tared_scale.py

- USB cable for Arduino connection```



## 👨‍🔬 Author Information## Load Cell Wiring

FX29 Load Cell → OpenScale:

**Johnny Hamnesjö Olausson**  - RED → RED (V+)

📧 Email: johnny.hamnesjo@chalmers.se  - BLACK → BLK (V-)

🏛️ Institution: Chalmers University of Technology  - YELLOW → WHT (O+)

📚 Department: Department of Industrial and Materials Science- WHITE → GRN (O-)



## 📚 Documentation## Useful Links

- [SparkFun OpenScale Product Page](https://www.sparkfun.com/products/13261)

See `FC2231_SYSTEM_GUIDE.md` for comprehensive setup and usage instructions.- [OpenScale Hookup Guide](https://learn.sparkfun.com/tutorials/openscale-hookup-guide)

- [OpenScale GitHub Repo](https://github.com/sparkfun/OpenScale)

## 📄 License

GNU General Public License v3.0 - See `LICENSE` file for details.

---
*Designed with kawaii precision and love* 🌸
