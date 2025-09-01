import serial
import time
import statistics

PORT = 'COM4'
BAUDRATE = 9600

def accuracy_test_and_calibration():
    print("=== OpenScale Accuracy Test & Calibration ===")
    print("This will help identify and fix accuracy issues")
    print("\nStep 1: Stability Test")
    print("Make sure load cell is clamped and NOTHING is on the free end")
    input("Press Enter to start stability test...")
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            # Skip initial messages
            time.sleep(2)
            for _ in range(10):
                ser.readline()
            
            print("Recording 50 empty readings to check stability...")
            empty_readings = []
            
            for i in range(50):
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and decoded.split(',')[0].isdigit():
                        parts = decoded.split(',')
                        if len(parts) >= 2:
                            raw_lbs = float(parts[1])
                            raw_grams = raw_lbs * 453.592
                            empty_readings.append(raw_grams)
                            if i % 10 == 0:
                                print(f"  Reading {i+1}/50: {raw_grams:.1f}g")
                time.sleep(0.2)
            
            empty_avg = statistics.mean(empty_readings)
            empty_std = statistics.stdev(empty_readings)
            empty_range = max(empty_readings) - min(empty_readings)
            
            print(f"\n📊 Stability Results:")
            print(f"   Average: {empty_avg:.2f}g")
            print(f"   Std Dev: {empty_std:.2f}g")
            print(f"   Range: {empty_range:.2f}g")
            
            if empty_std < 2:
                print("   ✅ Excellent stability")
            elif empty_std < 5:
                print("   ✅ Good stability")
            elif empty_std < 10:
                print("   ⚠️  Fair stability - check mounting")
            else:
                print("   ❌ Poor stability - check wiring/mounting")
            
            # Multi-point calibration
            print(f"\n\nStep 2: Multi-Point Calibration")
            print("We'll use multiple known weights to improve accuracy")
            
            calibration_points = []
            
            # Zero point
            print(f"\nCalibration Point 1: Empty (0g)")
            calibration_points.append((0, empty_avg))
            
            # Additional calibration points
            weights_to_test = [100, 500, 1000, 2000]  # grams
            
            for weight in weights_to_test:
                print(f"\nCalibration Point: {weight}g")
                input(f"Place exactly {weight}g on the load cell, then press Enter...")
                
                readings = []
                print(f"Recording 20 readings with {weight}g...")
                
                for i in range(20):
                    line = ser.readline()
                    if line:
                        decoded = line.decode('utf-8', errors='ignore').strip()
                        if ',' in decoded and decoded.split(',')[0].isdigit():
                            parts = decoded.split(',')
                            if len(parts) >= 2:
                                raw_lbs = float(parts[1])
                                raw_grams = raw_lbs * 453.592
                                readings.append(raw_grams)
                    time.sleep(0.2)
                
                if readings:
                    avg_reading = statistics.mean(readings)
                    std_reading = statistics.stdev(readings) if len(readings) > 1 else 0
                    calibration_points.append((weight, avg_reading))
                    print(f"   Average reading: {avg_reading:.2f}g (std: {std_reading:.2f})")
                else:
                    print(f"   ❌ No valid readings for {weight}g")
            
            # Calculate linear calibration
            print(f"\n🔧 Calibration Analysis:")
            print(f"Points collected: {len(calibration_points)}")
            
            if len(calibration_points) >= 2:
                # Simple linear regression
                weights = [point[0] for point in calibration_points]
                readings = [point[1] for point in calibration_points]
                
                # Calculate slope and intercept
                n = len(calibration_points)
                sum_w = sum(weights)
                sum_r = sum(readings)
                sum_wr = sum(w * r for w, r in zip(weights, readings))
                sum_ww = sum(w * w for w in weights)
                
                # Linear regression: weight = slope * reading + intercept
                slope = (n * sum_wr - sum_w * sum_r) / (n * sum(r * r for r in readings) - sum_r * sum_r)
                intercept = (sum_w - slope * sum_r) / n
                
                print(f"Linear calibration equation:")
                print(f"Weight (g) = {slope:.6f} * Reading + {intercept:.2f}")
                
                # Test accuracy
                print(f"\nAccuracy test:")
                for weight, reading in calibration_points:
                    calculated_weight = slope * reading + intercept
                    error = calculated_weight - weight
                    error_percent = (error / weight * 100) if weight > 0 else 0
                    print(f"  {weight}g: Calculated {calculated_weight:.1f}g, Error: {error:+.1f}g ({error_percent:+.1f}%)")
                
                # Create improved script
                script_content = f'''import serial
import time

PORT = 'COM4'
BAUDRATE = 9600

# Improved calibration parameters
SLOPE = {slope:.6f}
INTERCEPT = {intercept:.2f}

def accurate_readings():
    print("=== Accurate OpenScale Readings ===")
    print(f"Using improved calibration:")
    print(f"Weight = {{SLOPE:.6f}} * Reading + {{INTERCEPT:.2f}}")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            # Skip initial messages
            time.sleep(2)
            for _ in range(5):
                ser.readline()
            
            while True:
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and decoded.split(',')[0].isdigit():
                        parts = decoded.split(',')
                        if len(parts) >= 4:
                            reading_num = parts[0]
                            raw_lbs = float(parts[1])
                            temp = parts[3]
                            
                            # Convert and apply improved calibration
                            raw_grams = raw_lbs * 453.592
                            weight_grams = SLOPE * raw_grams + INTERCEPT
                            
                            # Display results
                            if abs(weight_grams) < 2:
                                status = "🎯 ZERO "
                                display_weight = 0.0
                            else:
                                status = "⚖️  WEIGHT"
                                display_weight = weight_grams
                            
                            print(f"{{status}} | #{{reading_num:>4}} | {{display_weight:>8.1f}}g | {{temp:>6}}°C")
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\\n✅ Stopped.")
    except Exception as e:
        print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    accurate_readings()'''
                
                with open('openscale-project/accurate_readings.py', 'w') as f:
                    f.write(script_content)
                
                print(f"\n✅ Created accurate_readings.py with improved calibration!")
                print(f"✅ Run: python accurate_readings.py")
                
            else:
                print("❌ Not enough calibration points collected")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    accuracy_test_and_calibration()
