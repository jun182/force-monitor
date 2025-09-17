# 🌸 Persistent Calibration System 🌸

## Overview

The Force Monitor now includes a sophisticated persistent calibration system that automatically saves and loads calibration data between sessions. **No more hardcoded values!**

## Features

✅ **Automatic save/load** - Calibration persists between restarts  
✅ **Smart tare calibration** - Quick zero-point adjustment  
✅ **Full weight calibration** - Scale factor calibration with known weights  
✅ **Calibration validation** - Checks data integrity and stability  
✅ **Backup system** - Automatic calibration backups  
✅ **Status monitoring** - Shows calibration age and quality  

## Files Modified

- **`calibration_manager.py`** - New persistent calibration system
- **`zen_terminal.py`** - Updated terminal interface with live calibration
- **`enhanced_gui.py`** - Updated GUI with calibration management
- **`test_calibration.py`** - Test script for the calibration system

## How It Works

### 1. Calibration Storage
Calibration data is stored in `force_monitor_calibration.json`:
```json
{
    "tare_offset": -33.9975,
    "scale_factor": 1.0,
    "calibration_date": "2025-09-02T16:06:22.581990",
    "calibration_stability": 1.31,
    "calibration_weight": 0.0,
    "serial_port": "COM4",
    "version": "2.0"
}
```

### 2. Terminal Interface (`zen_terminal.py`)

**New Features:**
- Shows calibration status at startup
- Press **'c'** during operation to recalibrate
- Automatic calibration loading
- Persistent tare offset between sessions

**Usage:**
```bash
python zen_terminal.py
```

### 3. GUI Interface (`enhanced_gui.py`)

**New Features:**
- Calibration status display at bottom
- Enhanced calibrate and tare buttons
- Automatic save/load of calibration
- Error handling for calibration failures

**Usage:**
```bash
python enhanced_gui.py
```

## Calibration Workflow

### Quick Tare (Zero Point)
1. Place nothing on the scale
2. Click **"🎯 Quick Tare"** (GUI) or press **'c'** (Terminal)
3. Calibration automatically saves to file

### Full Calibration (20-point average)
1. Place nothing on the scale
2. Click **"⚖️ Calibrate Zero"** (GUI) or press **'c'** (Terminal)
3. Wait for 20 readings to complete
4. System calculates stable zero point
5. Calibration automatically saves to file

### Weight Calibration (Future Feature)
- Use known weights to calibrate scale factor
- Improves accuracy across different weight ranges

## Benefits Over Old System

| Old System | New System |
|------------|------------|
| ❌ Hardcoded tare offset | ✅ Persistent calibration file |
| ❌ Edit code to change | ✅ Live recalibration |
| ❌ No stability tracking | ✅ Statistical stability analysis |
| ❌ No backup system | ✅ Automatic calibration backups |
| ❌ Single value storage | ✅ Complete calibration metadata |

## Calibration Status Indicators

- **🟢 Excellent** - Stability < 10g
- **🟡 Good** - Stability < 50g  
- **🟠 Fair** - Stability < 200g
- **🔴 Poor** - Stability > 200g

## Error Handling

The system gracefully handles:
- Missing calibration files (creates defaults)
- Corrupted calibration data (falls back to defaults)
- Serial communication errors during calibration
- Insufficient readings for calibration

## Testing

Run the test script to verify the system:
```bash
python test_calibration.py
```

This creates a test calibration and demonstrates all features without requiring hardware.

## Migration from Old System

1. **First run**: System automatically creates default calibration
2. **Old offset**: Your hardcoded value (-33.9975g) can be manually entered
3. **New calibration**: Perform fresh calibration for best accuracy

## Advanced Features

### Calibration Manager API
```python
from calibration_manager import CalibrationManager

# Create manager
cal_manager = CalibrationManager()

# Load calibration
cal_data = cal_manager.load_calibration()

# Apply to readings
calibrated_weight = cal_manager.apply_calibration(raw_weight, cal_data)

# Save new calibration
cal_manager.save_calibration(new_cal_data)
```

### Backup System
- Automatic backups before major calibrations
- Timestamped backup files
- Manual backup capability

## Troubleshooting

**Q: Calibration file not found?**  
A: System creates default calibration automatically

**Q: Calibration seems inaccurate?**  
A: Perform fresh calibration with stable environment

**Q: Can't save calibration?**  
A: Check file permissions in the project directory

**Q: Want to reset calibration?**  
A: Delete `force_monitor_calibration.json` and restart

---

## 🎌 Kawaii Precision Engineering 🎌

*Designed with love for accurate, persistent measurements!*

**Author:** Johnny Hamnesjö Olausson  
**Email:** johnny.hamnesjo@chalmers.se  
**Institution:** Chalmers University of Technology
