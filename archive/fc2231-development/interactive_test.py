#!/usr/bin/env python3
"""
🔧 Interactive FC2231 Console Test
Run this while the GUI is open to test port access
"""

import serial
import time
from fc2231_calibration_manager import FC2231CalibrationManager

def interactive_test():
    print("🔧 Interactive FC2231 Console Test")
    print("📱 This runs alongside the GUI to test port access")
    
    port = 'COM5'
    baudrate = 9600
    
    # Load calibration
    cal_manager = FC2231CalibrationManager()
    calibration_data = cal_manager.load_calibration()
    
    try:
        print(f"\n🔌 Connecting to {port}...")
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        print("✅ Connected! Reading 20 samples...")
        
        count = 0
        for i in range(20):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line and ',' in line and not line.startswith("FC2231,"):
                    parts = line.split(',')
                    if len(parts) >= 9:
                        try:
                            voltage = float(parts[1])
                            force = cal_manager.voltage_to_force(voltage, calibration_data)
                            count += 1
                            print(f"📊 [{count:2d}] {voltage:.3f}V → {force:.3f}N")
                        except:
                            pass
            time.sleep(0.2)
        
        ser.close()
        print(f"\n✅ Test complete! Got {count} readings")
        
        if count == 0:
            print("❌ No valid readings - this is the same problem the GUI has!")
        else:
            print("✅ Data is flowing - the issue is GUI-specific")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 This tells us if the port is busy or there's another issue")

if __name__ == "__main__":
    interactive_test()
    input("\nPress Enter to close...")