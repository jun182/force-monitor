#!/usr/bin/env python3
"""
Simple Arduino Connection Test
"""

import serial
import time

def test_arduino_connection():
    ports_to_try = ['COM5', 'COM4', 'COM3', 'COM6']
    
    for port in ports_to_try:
        try:
            print(f"🔍 Trying to connect to {port}...")
            with serial.Serial(port, 9600, timeout=2) as ser:
                print(f"✅ Connected to {port}!")
                
                # Wait for Arduino to initialize
                time.sleep(3)
                
                # Try to read some data
                print("📡 Listening for data...")
                for i in range(10):
                    try:
                        line = ser.readline()
                        if line:
                            decoded = line.decode('utf-8', errors='ignore').strip()
                            print(f"📨 Received: {decoded}")
                        else:
                            print(f"⏳ Waiting... ({i+1}/10)")
                        time.sleep(1)
                    except Exception as e:
                        print(f"⚠️  Read error: {e}")
                
                return True
                
        except serial.SerialException as e:
            print(f"❌ Failed to connect to {port}: {e}")
        except PermissionError as e:
            print(f"🔒 Permission denied for {port}: {e}")
            print("💡 Hint: Close Arduino IDE Serial Monitor if open")
        except Exception as e:
            print(f"⚠️  Unexpected error with {port}: {e}")
    
    print("❌ Could not connect to any port")
    return False

if __name__ == "__main__":
    print("🌸 Arduino Connection Test 🌸")
    test_arduino_connection()