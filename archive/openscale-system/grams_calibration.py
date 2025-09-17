import serial
import time
import statistics

PORT = 'COM4'
BAUDRATE = 9600

def grams_only_calibration():
    print("=== OpenScale Calibration - Grams Only ===")
    print("This calibration will work entirely in grams.")
    print("Step 1: Record baseline with empty load cell")
    print("Make sure there is NOTHING on the load cell!")
    input("Press Enter when ready...")
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            print("Recording empty baseline...")
            empty_readings = []
            
            # Skip initial messages
            time.sleep(2)
            for _ in range(10):
                ser.readline()
            
            # Collect empty readings
            for i in range(20):
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and decoded.split(',')[0].isdigit():
                        parts = decoded.split(',')
                        if len(parts) >= 2:
                            try:
                                # Get raw reading (still in lbs from device, but we'll convert)
                                raw_lbs = float(parts[1])
                                raw_grams = raw_lbs * 453.592  # Convert to grams immediately
                                empty_readings.append(raw_grams)
                                print(f"Empty reading {i+1}/20: {raw_grams:.1f} grams (raw)")
                            except ValueError:
                                pass
                time.sleep(0.3)
            
            if not empty_readings:
                print("❌ No valid readings!")
                return
            
            empty_baseline = statistics.mean(empty_readings)
            empty_std = statistics.stdev(empty_readings) if len(empty_readings) > 1 else 0
            
            print(f"\n📊 Empty Baseline:")
            print(f"   Average: {empty_baseline:.1f} grams")
            print(f"   Std Dev: {empty_std:.1f} grams")
            print(f"   Stability: {'Good' if empty_std < 50 else 'Fair' if empty_std < 200 else 'Poor'}")
            
            # Step 2: Calibration weight
            cal_weight = float(input("\nEnter calibration weight in GRAMS (e.g., 1000): "))
            print(f"Place exactly {cal_weight}g on the load cell...")
            input("Press Enter when weight is placed...")
            
            print("Recording loaded readings...")
            loaded_readings = []
            
            for i in range(20):
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and decoded.split(',')[0].isdigit():
                        parts = decoded.split(',')
                        if len(parts) >= 2:
                            try:
                                raw_lbs = float(parts[1])
                                raw_grams = raw_lbs * 453.592
                                loaded_readings.append(raw_grams)
                                print(f"Loaded reading {i+1}/20: {raw_grams:.1f} grams (raw)")
                            except ValueError:
                                pass
                time.sleep(0.3)
            
            loaded_baseline = statistics.mean(loaded_readings)
            loaded_std = statistics.stdev(loaded_readings) if len(loaded_readings) > 1 else 0
            
            print(f"\n📊 Loaded Results:")
            print(f"   Average: {loaded_baseline:.1f} grams")
            print(f"   Std Dev: {loaded_std:.1f} grams")
            
            # Calculate calibration in grams
            raw_change_grams = loaded_baseline - empty_baseline
            expected_change_grams = cal_weight
            scale_factor = raw_change_grams / expected_change_grams
            
            print(f"\n🔧 Calibration Results (All in Grams):")
            print(f"   Empty baseline: {empty_baseline:.1f} grams")
            print(f"   With {cal_weight}g: {loaded_baseline:.1f} grams")
            print(f"   Raw change: {raw_change_grams:.1f} grams")
            print(f"   Expected change: {expected_change_grams:.1f} grams")
            print(f"   Scale factor: {scale_factor:.6f}")
            
            if abs(scale_factor - 1.0) > 0.5:
                print("⚠️  Warning: Scale factor is far from 1.0 - check load cell orientation!")
            
            # Create new grams-only reading script
            script_content = f'''import serial
import time

PORT = 'COM4'
BAUDRATE = 9600

# Calibration data (all in grams)
EMPTY_BASELINE_GRAMS = {empty_baseline:.6f}
SCALE_FACTOR = {scale_factor:.6f}

def grams_readings():
    print("=== OpenScale - Grams Only ===")
    print(f"Empty baseline: {{EMPTY_BASELINE_GRAMS:.1f}} grams")
    print(f"Scale factor: {{SCALE_FACTOR:.3f}}")
    print("All measurements in GRAMS only!")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
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
                            
                            # Convert everything to grams
                            raw_grams = raw_lbs * 453.592
                            weight_change_grams = raw_grams - EMPTY_BASELINE_GRAMS
                            actual_weight_grams = weight_change_grams / SCALE_FACTOR
                            
                            # Display results
                            if abs(actual_weight_grams) < 2:  # Within 2g, consider zero
                                status = "🎯 ZERO "
                                display_weight = 0.0
                            else:
                                status = "⚖️  WEIGHT"
                                display_weight = actual_weight_grams
                            
                            print(f"{{status}} | #{{reading_num:>4}} | {{display_weight:>8.1f}}g | {{temp:>6}}°C")
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\\n✅ Stopped.")
    except Exception as e:
        print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    grams_readings()'''
            
            # Save the script
            with open('openscale-project/grams_only.py', 'w') as f:
                f.write(script_content)
            
            print(f"\n✅ Created grams_only.py - no pounds anywhere!")
            print(f"✅ Run: python openscale-project/grams_only.py")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    grams_only_calibration()
