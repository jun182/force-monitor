# FC2231 Force Monitor - Terminal Interface# 🌸 Force Monitor ~ Kawaii Edition 🌸



🌸 **Kawaii Arduino Force Sensor Monitoring System** 🌸**Precision Weight Measurement Interface**



A professional-grade force monitoring system using FC2231 amplified force sensors with Arduino Uno R3, featuring a beautiful terminal interface with CSV data export capabilities.## 👨‍🔬 Author Information



## 🚀 Quick Start**Johnny Hamnesjö Olausson**  

📧 Email: johnny.hamnesjo@chalmers.se  

1. **Install Dependencies**🏛️ Institution: Chalmers University of Technology  

   ```bash📚 Department: Department of Industrial and Materials Science

   pip install -r requirements.txt

   ```## 📄 License



2. **Connect Hardware**This project is licensed under the GNU General Public License v3.0.

   - FC2231 sensor to Arduino Uno R3 analog pin A0

   - Arduino connected via USB (auto-detected on COM5)This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.



3. **Run Terminal Monitor**🌸 *Designed with kawaii simplicity and precision* 🌸

   ```bash

   python fc2231_terminal.py## What is this project?

   ```This **Force Monitor** system interfaces with SparkFun OpenScale, a simple-to-use open source solution for measuring load cells and sending the data to your computer via serial (USB).



## 🎮 Controls## Getting Started

1. Connect your OpenScale to your PC via USB (should appear on COM4)

- **'C'** - Calibrate sensor (tare to zero)2. Install Python 3.x from https://www.python.org/

- **'E'** - Toggle CSV export recording  3. Install dependencies: `pip install -r requirements.txt`

- **'Q'** - Quit program gracefully4. Mount your load cell properly (clamp one end, load the other end)

- **Ctrl+C** - Emergency stop5. Run the enhanced GUI: `python enhanced_gui.py`



## 📊 Features## 🎌 Current Applications



- ✅ **Real-time force monitoring** with 5-second display intervals### **🌸 Enhanced GUI (Recommended)**

- ✅ **Professional CSV export** for data analysis- `enhanced_gui.py`: **Main GUI application** - Beautiful kawaii-inspired interface

- ✅ **Persistent calibration** system with JSON storage  - Real-time weight monitoring with cute aesthetics

- ✅ **Temperature monitoring** from sensor  - Session statistics (min/max/average)

- ✅ **Kawaii terminal aesthetics** with status indicators  - Precision calibration system

- ✅ **Session statistics** and data validation  - Data export to CSV

  - Kawaii-style interface with emojis

## 📁 File Structure

### **⛩️ Kawaii Terminal**

### Active System- `zen_terminal.py`: **Beautiful terminal interface** - Command line with kawaii styling

- `fc2231_terminal.py` - Main terminal interface  - Elegant display with emojis

- `fc2231_calibration_manager.py` - Calibration system  - Session statistics

- `fc2231_calibration.json` - Calibration data  - UwU-style status messages

- `FC2231_SYSTEM_GUIDE.md` - Detailed user guide

- `fc2231-datasheet.pdf` - Hardware specifications### **🔧 Utility Tools**

- `openscale_gui.py`: **Original GUI** - Basic visual interface

### Archive- `tared_scale.py`: **Terminal interface** - Command line monitoring

- `archive/openscale-system/` - Original OpenScale monitoring system- `tare_scale.py`: **Calibration tool** - Set new zero point

- `archive/fc2231-development/` - FC2231 development files and prototypes- `accurate_scale_monitor.py`: **Advanced terminal** - High precision monitoring

- `drift_monitor.py`: **Diagnostic tool** - Monitor stability over time

## 📈 CSV Export Format- `requirements.txt`: Python dependencies

- `calibration_data.txt`: Stored calibration parameters

Exported files include:- `drift_data.csv`: Drift analysis data

- Reading sequence numbers

- Full timestamps with milliseconds  ## Usage

- Voltage readings (V)### GUI Mode (Recommended)

- Force measurements (N and g)```bash

- Temperature data (°C)python openscale_gui.py

- Status classifications```

- Click "Start" to begin monitoring

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