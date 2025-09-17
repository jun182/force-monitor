#!/usr/bin/env python3
"""
Force Monitor - Enhanced Terminal
=================================

Author: Johnny Hamnesjö Olausson
Email: johnny.hamnesjo@chalmers.se
Institution: Chalmers University of Technology
Department: Department of Industrial and Materials Science

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import serial
import time
import statistics
import threading
import msvcrt
from collections import deque
from datetime import datetime
from calibration_manager import CalibrationManager

PORT = 'COM4'
BAUDRATE = 9600

class ZenScale:
    def __init__(self):
        # Load calibration from persistent storage
        self.cal_manager = CalibrationManager()
        self.calibration_data = self.cal_manager.load_calibration()
        self.readings_buffer = deque(maxlen=10)  # Rolling average
        self.session_weights = []
        self.session_start_time = datetime.now()
        
    def process_reading(self, raw_lbs, temp):
        """Process a raw reading with Zen-like precision"""
        # Convert to grams
        raw_grams = raw_lbs * 453.592
        
        # Apply calibration (tare and scale factor)
        weight_grams = self.cal_manager.apply_calibration(raw_grams, self.calibration_data)
        
        # Add to rolling buffer
        self.readings_buffer.append(weight_grams)
        
        # Calculate smoothed reading
        if len(self.readings_buffer) >= 3:
            smoothed = statistics.median(self.readings_buffer)
        else:
            smoothed = weight_grams
            
        # Zero detection with hysteresis
        if abs(smoothed) < 10:  # 10g threshold
            display_weight = 0.0
            status = "🌸 ZERO"
        else:
            display_weight = smoothed
            if display_weight > 0:
                status = "⚖️  WEIGHT"
            else:
                status = "🔻 NEGATIVE"
            
        # Add to session data
        self.session_weights.append(display_weight)
            
        return display_weight, status, temp
    
    def recalibrate_tare(self, raw_readings):
        """Perform live tare recalibration"""
        calibration_data = self.cal_manager.perform_tare_calibration(raw_readings)
        
        # Save new calibration
        if self.cal_manager.save_calibration(calibration_data):
            self.calibration_data = calibration_data
            return True
        return False

def show_header():
    """Display beautiful header with kawaii aesthetics"""
    print("\n" + "═" * 80)
    print("🌸" + " " * 30 + "Force Monitor ~ UwU" + " " * 30 + "🌸")
    print(" " * 23 + "Kawaii Precision Load Cell Interface")
    print("═" * 80)
    print()
    print("👨‍🔬 Author: Johnny Hamnesjö Olausson")
    print("📧 Email: johnny.hamnesjo@chalmers.se")
    print("🏛️  Institution: Chalmers University of Technology")
    print("📚 Department: Department of Industrial and Materials Science")
    print()
    print("📄 License: GNU General Public License v3.0")
    print("🌸 Designed with kawaii simplicity and precision 🌸")
    print("═" * 80)
    
def show_calibration_info(scale):
    """Display current calibration status"""
    cal_status = scale.cal_manager.get_calibration_status(scale.calibration_data)
    tare_offset = scale.calibration_data.get("tare_offset", 0.0)
    scale_factor = scale.calibration_data.get("scale_factor", 1.0)
    
    print(f"\n🔧 Calibration Status: {cal_status}")
    print(f"   ⚖️  Tare offset: {tare_offset:>8.2f}g")
    print(f"   📏 Scale factor: {scale_factor:>8.4f}")
    print("   💡 Tip: Press 'C' during operation to recalibrate")
    print()

def show_statistics(scale):
    """Display session statistics with kawaii styling"""
    if scale.session_weights:
        non_zero_weights = [w for w in scale.session_weights if abs(w) > 5]
        if non_zero_weights:
            print(f"\n📊 Session Statistics ~ UwU:")
            print(f"   📉 Minimum: {min(non_zero_weights):>8.1f}g")
            print(f"   📈 Maximum: {max(non_zero_weights):>8.1f}g") 
            print(f"   📊 Average: {statistics.mean(non_zero_weights):>8.1f}g")
            if len(non_zero_weights) > 1:
                print(f"   📏 Std Dev: {statistics.stdev(non_zero_weights):>8.1f}g")
            print(f"   🔢 Readings: {len(scale.session_weights):>8}")
            
            # Session duration
            duration = datetime.now() - scale.session_start_time
            minutes, seconds = divmod(duration.seconds, 60)
            print(f"   ⏱️  Duration: {minutes:>8}:{seconds:02d}")

def zen_scale_monitor():
    """Main monitoring function with kawaii aesthetics"""
    show_header()
    
    scale = ZenScale()
    show_calibration_info(scale)
    
    print("🎌 Starting Kawaii Scale Monitor... >w<")
    print("💡 Controls: Ctrl+C to stop")
    print("            Press 'c' key during operation to recalibrate")
    print("-" * 80)
    print("Reading# |  Raw(lbs) | Status      | Weight(g) | Temp(°C) | Time")
    print("-" * 80)
    
    calibration_request = False
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            # Skip startup messages
            time.sleep(2)
            for _ in range(10):
                ser.readline()
            
            reading_count = 0
            
            while True:
                # Check for user input (Windows compatible)
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == 'c':
                        calibration_request = True
                
                # Handle calibration request
                if calibration_request:
                    print(f"\n🌸 Calibration requested! 🌸")
                    if interactive_calibration(scale, ser):
                        print("✅ Calibration complete! Resuming monitoring...")
                        show_calibration_info(scale)
                        print("-" * 80)
                        print("Reading# |  Raw(lbs) | Status      | Weight(g) | Temp(°C) | Time")
                        print("-" * 80)
                    else:
                        print("❌ Calibration failed. Resuming monitoring...")
                        print("-" * 80)
                    calibration_request = False
                
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and 'lbs' in decoded:
                        parts = decoded.split(',')
                        if len(parts) >= 4 and parts[2] == 'lbs':
                            try:
                                reading_num = parts[0]
                                raw_lbs = float(parts[1])
                                temp = float(parts[3])
                                
                                # Process with kawaii precision
                                display_weight, status, temperature = scale.process_reading(raw_lbs, temp)
                                
                                # Current time
                                current_time = datetime.now().strftime('%H:%M:%S')
                                
                                # Display with kawaii aesthetics
                                if "ZERO" in status:
                                    weight_display = "    0.0"
                                else:
                                    weight_display = f"{display_weight:7.1f}"
                                
                                print(f"{reading_num:>7} | {raw_lbs:>8.2f} | {status:<11} | {weight_display}g | {temperature:>6.1f}° | {current_time}")
                                
                                reading_count += 1
                                
                                # Periodic statistics display
                                if reading_count % 100 == 0:
                                    show_statistics(scale)
                                    print("-" * 80)
                                
                            except (ValueError, IndexError):
                                pass
                
                time.sleep(0.1)

def interactive_calibration(scale, ser):
    """Interactive calibration routine"""
    print(f"\n🌸 Kawaii Calibration Mode 🌸")
    print("Make sure the load cell is empty and stable!")
    print("This will take 20 readings to establish a new zero point.")
    
    response = input("Continue with calibration? (y/N): ").lower().strip()
    if response != 'y':
        print("Calibration cancelled.")
        return False
    
    print("📊 Taking 20 calibration readings...")
    calibration_readings = []
    
    try:
        for i in range(20):
            line = ser.readline()
            if line:
                decoded = line.decode('utf-8', errors='ignore').strip()
                if ',' in decoded and 'lbs' in decoded:
                    parts = decoded.split(',')
                    if len(parts) >= 4 and parts[2] == 'lbs':
                        try:
                            raw_lbs = float(parts[1])
                            raw_grams = raw_lbs * 453.592
                            calibration_readings.append(raw_grams)
                            print(f"  📍 Reading {i+1}/20: {raw_grams:.2f}g")
                        except (ValueError, IndexError):
                            pass
            time.sleep(0.3)
        
        if len(calibration_readings) >= 10:
            success = scale.recalibrate_tare(calibration_readings)
            if success:
                stability = statistics.stdev(calibration_readings)
                print(f"\n✅ Calibration Complete!")
                print(f"   📊 New tare offset: {scale.calibration_data['tare_offset']:.2f}g")
                print(f"   📏 Stability: ±{stability:.2f}g")
                print(f"   💾 Saved to calibration file")
                return True
            else:
                print(f"❌ Failed to save calibration")
                return False
        else:
            print(f"❌ Insufficient readings for calibration")
            return False
            
    except Exception as e:
        print(f"❌ Calibration error: {e}")
        return False
                
    except KeyboardInterrupt:
        print(f"\n\n🌸 Kawaii Session Complete! >w< 🌸")
        show_statistics(scale)
        print(f"\n🙏 Thank you for using Force Monitor! UwU 🙏")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    zen_scale_monitor()
