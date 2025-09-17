# Archive Directory Structure

This directory contains archived files that are not needed for the main FC2231 terminal system.

## 📁 openscale-system/
Contains all files related to the original OpenScale force monitoring system:
- `accuracy_test.py` - OpenScale accuracy testing
- `accurate_scale_monitor.py` - Enhanced OpenScale monitor
- `calibration_manager.py` - OpenScale calibration system
- `CALIBRATION_SYSTEM.md` - OpenScale calibration documentation
- `drift_monitor.py` - OpenScale drift monitoring
- `enhanced_gui.py` - OpenScale GUI interface
- `grams_calibration.py` - OpenScale gram calibration
- `proper_tare.py` - OpenScale tare functionality
- `raw_data_analyzer.py` - OpenScale data analysis
- `read_openscale.py` - Basic OpenScale reader
- `tared_scale.py` - OpenScale tared measurements
- `tare_scale.py` - OpenScale tare operations
- `zen_terminal.py` - OpenScale zen interface
- `force_monitor_calibration.json` - OpenScale calibration data

## 📁 fc2231-development/
Contains FC2231 development files, prototypes, and test utilities:
- `debug_gui_connection.py` - GUI connection debugging
- `fc2231_arduino_sketch.ino` - Arduino sketch (complex version)
- `fc2231_gui.py` - Full GUI with drift monitoring (had bugs)
- `interactive_test.py` - Interactive testing utility
- `simple_fc2231_gui.py` - Simplified GUI test
- `test_arduino_connection.py` - Arduino connection tester
- `test_calibration.json` - Test calibration data
- `test_calibration.py` - Calibration testing
- `test_csv_export.py` - CSV export testing
- `working_fc2231_gui.py` - Working GUI version
- `fc2231_simple/` - Simplified Arduino sketch folder
- `FC2231_Force_Data_20250917_105732.csv` - Test export file

## 🚀 Active System (Main Directory)
The main directory now contains only the essential FC2231 terminal system:
- `fc2231_terminal.py` - Main terminal interface
- `fc2231_calibration_manager.py` - Calibration system
- `fc2231_calibration.json` - Active calibration data
- `FC2231_SYSTEM_GUIDE.md` - User documentation
- `fc2231-datasheet.pdf` - Hardware reference
- `requirements.txt` - Python dependencies
- `README.md` - Project overview
- `LICENSE` - GNU GPL v3 license

This organization keeps the main directory clean while preserving all development history.