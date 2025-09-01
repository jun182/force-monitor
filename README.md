# 🌸 Force Monitor ~ Kawaii Edition 🌸

**Precision Weight Measurement Interface**

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
This **Force Monitor** system interfaces with SparkFun OpenScale, a simple-to-use open source solution for measuring load cells and sending the data to your computer via serial (USB).

## Getting Started
1. Connect your OpenScale to your PC via USB (should appear on COM4)
2. Install Python 3.x from https://www.python.org/
3. Install dependencies: `pip install -r requirements.txt`
4. Mount your load cell properly (clamp one end, load the other end)
5. Run the enhanced GUI: `python enhanced_gui.py`

## 🎌 Current Applications

### **🌸 Enhanced GUI (Recommended)**
- `enhanced_gui.py`: **Main GUI application** - Beautiful kawaii-inspired interface
  - Real-time weight monitoring with cute aesthetics
  - Session statistics (min/max/average)
  - Precision calibration system
  - Data export to CSV
  - Kawaii-style interface with emojis

### **⛩️ Kawaii Terminal**
- `zen_terminal.py`: **Beautiful terminal interface** - Command line with kawaii styling
  - Elegant display with emojis
  - Session statistics
  - UwU-style status messages

### **🔧 Utility Tools**
- `openscale_gui.py`: **Original GUI** - Basic visual interface
- `tared_scale.py`: **Terminal interface** - Command line monitoring
- `tare_scale.py`: **Calibration tool** - Set new zero point
- `accurate_scale_monitor.py`: **Advanced terminal** - High precision monitoring
- `drift_monitor.py`: **Diagnostic tool** - Monitor stability over time
- `requirements.txt`: Python dependencies
- `calibration_data.txt`: Stored calibration parameters
- `drift_data.csv`: Drift analysis data

## Usage
### GUI Mode (Recommended)
```bash
python openscale_gui.py
```
- Click "Start" to begin monitoring
- Click "Tare (Zero)" to reset zero point
- Place objects on load cell to measure weight

### Terminal Mode
```bash
python tared_scale.py
```

## Load Cell Wiring
FX29 Load Cell → OpenScale:
- RED → RED (V+)
- BLACK → BLK (V-)
- YELLOW → WHT (O+)
- WHITE → GRN (O-)

## Useful Links
- [SparkFun OpenScale Product Page](https://www.sparkfun.com/products/13261)
- [OpenScale Hookup Guide](https://learn.sparkfun.com/tutorials/openscale-hookup-guide)
- [OpenScale GitHub Repo](https://github.com/sparkfun/OpenScale)
