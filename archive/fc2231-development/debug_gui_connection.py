#!/usr/bin/env python3
"""
🔧 FC2231 GUI Connection Debug Tool
Helps diagnose GUI connection issues
"""

import serial
import time
import threading

def test_gui_connection():
    """Test the exact same connection method the GUI uses"""
    port = 'COM5'
    baudrate = 9600
    
    print("🔧 GUI Connection Debug Tool")
    print(f"📡 Testing connection to {port} at {baudrate} baud...")
    
    try:
        # Exact same method as GUI
        serial_connection = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        
        print("✅ Serial connection established!")
        print("📨 Listening for data (10 seconds)...")
        
        start_time = time.time()
        received_count = 0
        
        while time.time() - start_time < 10:
            if serial_connection.in_waiting > 0:
                try:
                    line = serial_connection.readline().decode('utf-8').strip()
                    if line:
                        received_count += 1
                        print(f"📨 [{received_count}] {line}")
                        
                        # Try to parse like the GUI does
                        parts = line.split(',')
                        if len(parts) >= 9:
                            voltage = float(parts[1])
                            print(f"    💡 Parsed voltage: {voltage:.3f}V")
                            
                except Exception as e:
                    print(f"    ⚠️ Parse error: {e}")
            
            time.sleep(0.1)
        
        serial_connection.close()
        print(f"\n✅ Test complete! Received {received_count} messages")
        
        if received_count == 0:
            print("❌ No data received - this explains why GUI shows no readings!")
        else:
            print("✅ Data is flowing - GUI should work!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Make sure Arduino IDE Serial Monitor is closed")
        print("2. Make sure no other programs are using COM5")
        print("3. Try unplugging and reconnecting the Arduino")

if __name__ == "__main__":
    test_gui_connection()