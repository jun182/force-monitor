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
from collections import deque
from datetime import datetime

PORT = 'COM4'
BAUDRATE = 9600

class ZenScale:
    def __init__(self):
        self.tare_offset = -33.9975  # From accurate calibration
        self.readings_buffer = deque(maxlen=10)  # Rolling average
        self.session_weights = []
        self.session_start_time = datetime.now()
        
    def process_reading(self, raw_lbs, temp):
        """Process a raw reading with Zen-like precision"""
        # Convert and apply tare
        raw_grams = raw_lbs * 453.592
        weight_grams = raw_grams - self.tare_offset
        
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
    
    print("🎌 Starting Kawaii Scale Monitor... >w<")
    print("Press Ctrl+C to stop")
    print("-" * 80)
    print("Reading# |  Raw(lbs) | Status      | Weight(g) | Temp(°C) | Time")
    print("-" * 80)
    
    scale = ZenScale()
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            # Skip startup messages
            time.sleep(2)
            for _ in range(10):
                ser.readline()
            
            reading_count = 0
            
            while True:
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
                
    except KeyboardInterrupt:
        print(f"\n\n🌸 Kawaii Session Complete! >w< 🌸")
        show_statistics(scale)
        print(f"\n🙏 Thank you for using Force Monitor! UwU 🙏")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    zen_scale_monitor()
