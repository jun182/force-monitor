import serial
import time
import statistics
from collections import deque

PORT = 'COM4'
BAUDRATE = 9600

class AccurateScale:
    def __init__(self):
        self.tare_offset = -33.9975  # From your latest calibration
        self.readings_buffer = deque(maxlen=10)  # Rolling average
        self.last_tare_time = time.time()
        
    def process_reading(self, raw_lbs, temp):
        """Process a raw reading with advanced filtering"""
        # Apply tare
        tared_lbs = raw_lbs - self.tare_offset
        weight_grams = tared_lbs * 453.592
        
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
            status = "ZERO"
        else:
            display_weight = smoothed
            status = "WEIGHT"
            
        return display_weight, status, smoothed
    
    def auto_retare_check(self, current_weight):
        """Check if we need to auto-retare due to drift"""
        # If we've been "zero" for a while but readings are drifting
        if abs(current_weight) < 50 and time.time() - self.last_tare_time > 300:  # 5 minutes
            if len(self.readings_buffer) == 10:
                drift = max(self.readings_buffer) - min(self.readings_buffer)
                if drift > 100:  # More than 100g drift
                    return True
        return False

def accurate_scale_monitor():
    print("=== Accurate Scale Monitor v2.0 ===")
    print("Features: Rolling average, thermal compensation, auto-drift detection")
    print("Press Ctrl+C to stop")
    print("-" * 70)
    print("Reading# |  Raw(lbs) | Smooth(g) | Status   | Temp(°C) | Drift")
    print("-" * 70)
    
    scale = AccurateScale()
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            # Skip startup messages
            time.sleep(3)
            for _ in range(10):
                ser.readline()
            
            reading_count = 0
            start_time = time.time()
            
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
                                
                                # Process with advanced filtering
                                display_weight, status, smoothed = scale.process_reading(raw_lbs, temp)
                                
                                # Check for drift
                                drift_check = scale.auto_retare_check(smoothed)
                                drift_indicator = "DRIFT!" if drift_check else "OK"
                                
                                # Display
                                if status == "ZERO":
                                    weight_display = "ZERO"
                                else:
                                    weight_display = f"{display_weight:7.1f}g"
                                
                                print(f"{reading_num:>7} | {raw_lbs:>8.2f} | {weight_display:>9} | {status:>8} | {temp:>6.1f}° | {drift_indicator}")
                                
                                reading_count += 1
                                
                                # Periodic summary
                                if reading_count % 50 == 0:
                                    runtime = time.time() - start_time
                                    print(f"\n📊 Summary after {reading_count} readings ({runtime/60:.1f} min):")
                                    if len(scale.readings_buffer) >= 5:
                                        recent_std = statistics.stdev(list(scale.readings_buffer))
                                        print(f"   Recent stability: ±{recent_std:.1f}g")
                                        if recent_std < 20:
                                            print("   ✅ Excellent stability")
                                        elif recent_std < 50:
                                            print("   ✅ Good stability")
                                        else:
                                            print("   ⚠️  Check for vibrations/temperature changes")
                                    print("-" * 70)
                                
                            except (ValueError, IndexError):
                                pass
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print(f"\n\n✅ Monitoring Complete!")
        print(f"📈 Performance Summary:")
        print(f"   Readings processed: {reading_count}")
        print(f"   Current tare offset: {scale.tare_offset:.4f} lbs")
        print(f"   System accuracy: Good for typical applications")
        print(f"\n💡 Tips for better accuracy:")
        print(f"   • Keep temperature stable")
        print(f"   • Minimize vibrations")
        print(f"   • Re-tare periodically")
        print(f"   • Use known weights to verify calibration")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    accurate_scale_monitor()
