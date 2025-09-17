#!/usr/bin/env python3
"""
FC2231 Force Monitor - Kawaii Terminal Interface
===============================================

Author: Johnny Hamnesjö Olausson
Email: johnny.hamnesjo@chalmers.se
Institution: Chalmers University of Technology
Department: Department of Industrial and Materials Science

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import serial
import serial.tools.list_ports
import time
import statistics
import msvcrt
import csv
from collections import deque
from datetime import datetime
from fc2231_calibration_manager import FC2231CalibrationManager

# Default Arduino connection (adjust if needed)
PORT = 'COM5'  # Arduino detected on COM5
BAUDRATE = 9600

def find_arduino_port():
    """
    Auto-detect Arduino port by scanning available COM ports
    Returns the first port that responds like an Arduino, or None if not found
    """
    print("🔍 Scanning for Arduino...")
    
    # Get list of available COM ports
    available_ports = serial.tools.list_ports.comports()
    
    if not available_ports:
        print("❌ No COM ports found!")
        return None
    
    print(f"📡 Found {len(available_ports)} COM port(s):")
    for port in available_ports:
        print(f"   - {port.device}: {port.description}")
    
    # Try each port to see if Arduino responds
    for port in available_ports:
        try:
            print(f"🌸 Trying {port.device}...")
            
            # Try to connect
            with serial.Serial(port.device, BAUDRATE, timeout=3) as ser:
                time.sleep(2)  # Give Arduino time to initialize
                
                # Clear any initial data
                ser.flushInput()
                time.sleep(0.5)
                
                # Try to read some data
                for attempt in range(5):
                    try:
                        line = ser.readline()
                        if line:
                            decoded = line.decode('utf-8', errors='ignore').strip()
                            print(f"   📨 Received: {decoded[:50]}...")
                            
                            # Check if it looks like Arduino sensor data
                            if ',' in decoded and len(decoded.split(',')) >= 2:
                                print(f"✅ Arduino found on {port.device}!")
                                return port.device
                    except:
                        pass
                    time.sleep(0.5)
                        
        except serial.SerialException:
            print(f"   ❌ Could not connect to {port.device}")
            continue
        except Exception as e:
            print(f"   ⚠️  Error testing {port.device}: {e}")
            continue
    
    print("❌ No Arduino detected on any COM port")
    return None

class KawaiiFC2231Monitor:
    def __init__(self):
        # Load calibration from persistent storage
        self.cal_manager = FC2231CalibrationManager()
        self.calibration_data = self.cal_manager.load_calibration()
        
        # Data buffers
        self.voltage_buffer = deque(maxlen=10)  # Rolling average
        self.force_buffer = deque(maxlen=10)
        self.session_forces = []
        self.session_start_time = datetime.now()
        
        # Statistics
        self.reading_count = 0
        self.last_voltage = 0.0
        self.last_force_n = 0.0
        self.last_force_g = 0.0
        
        # Display timing
        self.last_display_time = 0
        
        # CSV export data
        self.export_data = []
        self.export_enabled = False
        
    def process_arduino_data(self, line):
        """Process data line from Arduino"""
        try:
            # Expected format: reading,voltage,V,temp,force_N,N,force_g,g,timestamp
            parts = line.strip().split(',')
            if len(parts) >= 9:
                reading_num = parts[0]
                voltage = float(parts[1])
                temp = float(parts[3])
                timestamp = parts[8]
                
                # Apply our calibration
                force_newtons = self.cal_manager.voltage_to_force(voltage, self.calibration_data)
                force_grams = self.cal_manager.force_to_grams(force_newtons)
                
                # Add to buffers
                self.voltage_buffer.append(voltage)
                self.force_buffer.append(force_newtons)
                
                # Calculate smoothed values
                if len(self.voltage_buffer) >= 3:
                    smoothed_voltage = statistics.median(self.voltage_buffer)
                    smoothed_force = statistics.median(self.force_buffer)
                else:
                    smoothed_voltage = voltage
                    smoothed_force = force_newtons
                
                # Update session data
                self.session_forces.append(smoothed_force)
                self.last_voltage = smoothed_voltage
                self.last_force_n = smoothed_force
                self.last_force_g = self.cal_manager.force_to_grams(smoothed_force)
                
                # Determine status with kawaii styling
                if abs(smoothed_force) < 0.1:  # Less than 0.1N
                    status = "🌸 ZERO"
                    force_display = "  0.00"
                elif smoothed_force > 0:
                    if smoothed_force < 1.0:
                        status = "⚖️  LIGHT"
                    elif smoothed_force < 10.0:
                        status = "💪 MEDIUM"
                    else:
                        status = "🔥 STRONG"
                    force_display = f"{smoothed_force:6.2f}"
                else:
                    status = "🔻 NEGATIVE"
                    force_display = f"{smoothed_force:6.2f}"
                
                self.reading_count += 1
                current_time = datetime.now().strftime('%H:%M:%S')
                current_datetime = datetime.now()
                
                # Store data for CSV export if enabled
                if self.export_enabled:
                    self.export_data.append({
                        'Reading#': reading_num,
                        'DateTime': current_datetime,
                        'Time': current_time,
                        'Voltage(V)': smoothed_voltage,
                        'Force(N)': smoothed_force,
                        'Force(g)': self.last_force_g,
                        'Temperature(°C)': temp,
                        'Status': status.replace('🌸 ', '').replace('⚖️  ', '').replace('💪 ', '').replace('🔥 ', '').replace('🔻 ', '')
                    })
                
                # Only display every 5 seconds
                current_timestamp = time.time()
                if current_timestamp - self.last_display_time >= 5.0:
                    # Display with kawaii aesthetics
                    print(f"{reading_num:>7} | {smoothed_voltage:>6.3f}V | {status:<10} | {force_display}N | {self.last_force_g:>7.1f}g | {temp:>5.1f}° | {current_time}")
                    self.last_display_time = current_timestamp
                
                return True
                
        except (ValueError, IndexError) as e:
            # Ignore invalid lines
            pass
        
        return False
    
    def send_arduino_command(self, ser, command):
        """Send command to Arduino"""
        ser.write(f"{command}\n".encode())
        time.sleep(0.1)
    
    def perform_tare_calibration(self, ser):
        """Perform tare calibration using Arduino"""
        print(f"\n🌸 Kawaii Tare Calibration 🌸")
        print("Make sure no force is applied to the sensor!")
        print("Arduino will take 20 readings for calibration...")
        
        response = input("Continue with tare calibration? (y/N): ").lower().strip()
        if response != 'y':
            print("Calibration cancelled.")
            return False
        
        # Send tare command to Arduino
        self.send_arduino_command(ser, "TARE")
        
        # Collect calibration data from Arduino
        voltage_readings = []
        calibration_complete = False
        start_time = time.time()
        
        print("📊 Collecting calibration data from Arduino...")
        
        while not calibration_complete and (time.time() - start_time) < 30:  # 30 second timeout
            try:
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if decoded.startswith("FC2231,TARE,"):
                        parts = decoded.split(',')
                        if "READING" in parts[2]:
                            # Extract voltage from reading
                            voltage_str = parts[4].replace('V', '')
                            voltage = float(voltage_str)
                            voltage_readings.append(voltage)
                            print(f"  📍 Reading {len(voltage_readings)}/20: {voltage:.4f}V")
                        elif "COMPLETE" in parts[2]:
                            calibration_complete = True
                            print(f"✅ Arduino calibration complete!")
                            
                            # Extract Arduino's calculated values
                            for part in parts[3:]:
                                if part.startswith("Voltage="):
                                    arduino_tare = float(part.split('=')[1].replace('V', ''))
                                elif part.startswith("StdDev="):
                                    arduino_stdev = float(part.split('=')[1].replace('V', ''))
                            
                            print(f"   📊 Arduino tare: {arduino_tare:.4f}V")
                            print(f"   📏 Arduino stability: ±{arduino_stdev:.4f}V")
                            
                            # Update our calibration
                            if len(voltage_readings) >= 10:
                                new_calibration = self.cal_manager.perform_voltage_tare(voltage_readings)
                                
                                if self.cal_manager.save_calibration(new_calibration):
                                    self.calibration_data = new_calibration
                                    print(f"   💾 Python calibration saved!")
                                    return True
                                else:
                                    print(f"   ❌ Failed to save Python calibration")
                                    return False
                            else:
                                print(f"   ❌ Insufficient readings for Python calibration")
                                return False
            except Exception as e:
                print(f"   ⚠️  Error during calibration: {e}")
                continue
        
        if not calibration_complete:
            print(f"❌ Calibration timed out")
            return False
        
        return True

    def export_to_csv(self):
        """Export collected data to CSV file"""
        if not self.export_data:
            print("📊 No data to export!")
            return False
            
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"FC2231_Force_Data_{timestamp}.csv"
            
            # Write CSV file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV columns
                fieldnames = [
                    'Reading#', 'DateTime', 'Time', 'Voltage(V)', 
                    'Force(N)', 'Force(g)', 'Temperature(°C)', 'Status'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data rows
                for row in self.export_data:
                    # Format datetime for CSV
                    row_copy = row.copy()
                    row_copy['DateTime'] = row['DateTime'].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Include milliseconds
                    writer.writerow(row_copy)
            
            print(f"✅ Data exported to: {filename}")
            print(f"📊 Total records: {len(self.export_data)}")
            print(f"📁 File opens in Excel, Google Sheets, or any text editor")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

def show_header():
    """Display beautiful header with kawaii aesthetics"""
    print("\n" + "═" * 80)
    print("🌸" + " " * 25 + "FC2231 Force Monitor ~ UwU" + " " * 25 + "🌸")
    print(" " * 20 + "Kawaii Arduino Force Sensor Interface")
    print("═" * 80)
    print()
    print("👨‍🔬 Author: Johnny Hamnesjö Olausson")
    print("📧 Email: johnny.hamnesjo@chalmers.se")
    print("🏛️  Institution: Chalmers University of Technology")
    print("📚 Department: Department of Industrial and Materials Science")
    print()
    print("📄 License: GNU General Public License v3.0")
    print("🔌 Sensor: FC2231 Amplified Force Sensor")
    print("🤖 Hardware: Arduino Uno R3")
    print("🌸 Designed with kawaii precision and love 🌸")
    print("═" * 80)

def show_calibration_info(monitor):
    """Display current calibration status"""
    cal_status = monitor.cal_manager.get_calibration_status(monitor.calibration_data)
    tare_voltage = monitor.calibration_data.get("tare_voltage", 0.5)
    max_force = monitor.calibration_data.get("max_force_newtons", 100.0)
    
    print(f"\n🔧 Calibration Status: {cal_status}")
    print(f"   ⚡ Tare voltage: {tare_voltage:>8.4f}V")
    print(f"   💪 Max force: {max_force:>8.1f}N ({monitor.cal_manager.force_to_grams(max_force):.0f}g)")
    print("   💡 Tip: Press 'c' during operation to recalibrate")
    print()

def show_statistics(monitor):
    """Display session statistics with kawaii styling"""
    if monitor.session_forces:
        non_zero_forces = [f for f in monitor.session_forces if abs(f) > 0.05]  # >0.05N threshold
        if non_zero_forces:
            print(f"\n📊 Session Statistics ~ UwU:")
            print(f"   📉 Minimum: {min(non_zero_forces):>8.2f}N ({monitor.cal_manager.force_to_grams(min(non_zero_forces)):>6.0f}g)")
            print(f"   📈 Maximum: {max(non_zero_forces):>8.2f}N ({monitor.cal_manager.force_to_grams(max(non_zero_forces)):>6.0f}g)")
            print(f"   📊 Average: {statistics.mean(non_zero_forces):>8.2f}N ({monitor.cal_manager.force_to_grams(statistics.mean(non_zero_forces)):>6.0f}g)")
            if len(non_zero_forces) > 1:
                std_dev = statistics.stdev(non_zero_forces)
                print(f"   📏 Std Dev: {std_dev:>8.2f}N ({monitor.cal_manager.force_to_grams(std_dev):>6.0f}g)")
            print(f"   🔢 Readings: {monitor.reading_count:>8}")
            
            # Session duration
            duration = datetime.now() - monitor.session_start_time
            minutes, seconds = divmod(duration.seconds, 60)
            print(f"   ⏱️  Duration: {minutes:>8}:{seconds:02d}")

def fc2231_monitor():
    """Main monitoring function with kawaii aesthetics"""
    show_header()
    
    monitor = KawaiiFC2231Monitor()
    show_calibration_info(monitor)
    
    print("🎌 Starting Kawaii FC2231 Monitor... >w<")
    print("💡 Controls: Ctrl+C or 'q' to stop")
    print("            Press 'c' key during operation to recalibrate")
    print("            Press 'e' key to toggle CSV export recording")
    print("-" * 80)
    print("Reading# | Voltage | Status     | Force(N) | Force(g) | Temp  | Time")
    print("-" * 80)
    
    calibration_request = False
    
    # Auto-detect Arduino port
    detected_port = find_arduino_port()
    if not detected_port:
        print(f"\n❌ No Arduino detected!")
        print(f"💡 Please check:")
        print(f"   - Arduino is connected via USB")
        print(f"   - Arduino has the FC2231 sketch uploaded")
        print(f"   - USB drivers are installed")
        print(f"   - Arduino IDE is not using the port")
        return
    
    print(f"\n🌸 Using Arduino on port: {detected_port} 🌸")
    
    try:
        with serial.Serial(detected_port, BAUDRATE, timeout=2) as ser:
            # Wait for Arduino startup
            print("🤖 Waiting for Arduino startup...")
            time.sleep(3)
            
            # Clear any startup messages
            for _ in range(20):
                try:
                    line = ser.readline()
                    if line:
                        decoded = line.decode('utf-8', errors='ignore').strip()
                        if decoded.startswith("FC2231,READY"):
                            print("✅ Arduino FC2231 ready!")
                            break
                except:
                    pass
            
            while True:
                # Check for user input (Windows compatible)
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == 'c':
                        calibration_request = True
                    elif key == 'e':
                        monitor.export_enabled = not monitor.export_enabled
                        if monitor.export_enabled:
                            print(f"\n📊 CSV export ENABLED - Recording data for export...")
                            monitor.export_data = []  # Clear previous data
                        else:
                            print(f"\n📊 CSV export DISABLED")
                        print("-" * 80)
                    elif key == 'q':
                        print(f"\n👋 Quit requested by user")
                        break
                
                # Handle calibration request
                if calibration_request:
                    print(f"\n🌸 Calibration requested! 🌸")
                    if monitor.perform_tare_calibration(ser):
                        print("✅ Calibration complete! Resuming monitoring...")
                        show_calibration_info(monitor)
                        print("-" * 80)
                        print("Reading# | Voltage | Status     | Force(N) | Force(g) | Temp  | Time")
                        print("-" * 80)
                    else:
                        print("❌ Calibration failed. Resuming monitoring...")
                        print("-" * 80)
                    calibration_request = False
                
                # Read data from Arduino
                try:
                    line = ser.readline()
                    if line:
                        decoded = line.decode('utf-8', errors='ignore').strip()
                        
                        # Process data lines (skip command responses)
                        if not decoded.startswith("FC2231,") and ',' in decoded:
                            monitor.process_arduino_data(decoded)
                            
                            # Periodic statistics display
                            if monitor.reading_count % 100 == 0:
                                show_statistics(monitor)
                                print("-" * 80)
                        
                except serial.SerialTimeoutException:
                    pass
                except Exception as e:
                    print(f"⚠️  Serial error: {e}")
                    time.sleep(1)
                
                time.sleep(0.01)  # Small delay to prevent CPU overload
                
    except KeyboardInterrupt:
        print(f"\n\n🌸 Kawaii FC2231 Session Complete! >w< 🌸")
        show_statistics(monitor)
        
        # Offer CSV export if data was recorded
        if monitor.export_data:
            print(f"\n📊 {len(monitor.export_data)} data points recorded for export")
            response = input("Export to CSV? (y/N): ").lower()
            if response in ['y', 'yes']:
                monitor.export_to_csv()
        
        print(f"\n🙏 Thank you for using FC2231 Force Monitor! UwU 🙏")
        print("=" * 80)
    except serial.SerialException as e:
        print(f"\n❌ Serial connection error: {e}")
        print(f"💡 Make sure Arduino is connected and accessible")
        print(f"💡 Try restarting the program to re-detect the port")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    fc2231_monitor()