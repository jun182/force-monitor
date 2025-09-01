import serial
import time
import statistics

PORT = 'COM4'
BAUDRATE = 9600

def tare_scale():
    print("=== Taring OpenScale (Setting Zero Point) ===")
    print("Make sure there is NOTHING on the load cell!")
    input("Press Enter to tare the scale...")
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            print("Recording current readings to set as zero...")
            tare_readings = []
            
            # Skip initial messages
            time.sleep(2)
            for _ in range(10):
                ser.readline()
            
            # Collect current readings for tare
            for i in range(15):
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and decoded.split(',')[0].isdigit():
                        parts = decoded.split(',')
                        if len(parts) >= 2:
                            try:
                                raw_lbs = float(parts[1])
                                raw_grams = raw_lbs * 453.592
                                tare_readings.append(raw_grams)
                                print(f"Tare reading {i+1}/15: {raw_grams:.1f} grams")
                            except ValueError:
                                pass
                time.sleep(0.2)
            
            if not tare_readings:
                print("❌ No valid readings!")
                return
            
            tare_point = statistics.mean(tare_readings)
            tare_std = statistics.stdev(tare_readings) if len(tare_readings) > 1 else 0
            
            print(f"\n📊 Tare Results:")
            print(f"   New zero point: {tare_point:.1f} grams")
            print(f"   Stability: {tare_std:.1f} grams")
            
            # Create tared reading script
            script_content = f'''import serial
import time

PORT = 'COM4'
BAUDRATE = 9600

# Tared zero point
TARE_POINT_GRAMS = {tare_point:.6f}

def tared_readings():
    print("=== OpenScale - Tared to Zero ===")
    print(f"Zero point: {{TARE_POINT_GRAMS:.1f}} grams")
    print("Scale is now zeroed!")
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
                            
                            # Convert to grams and subtract tare point
                            raw_grams = raw_lbs * 453.592
                            weight_grams = raw_grams - TARE_POINT_GRAMS
                            
                            # Display results
                            if abs(weight_grams) < 5:  # Within 5g, show as zero
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
    tared_readings()'''
            
            # Save the tared script
            with open('openscale-project/tared_scale.py', 'w') as f:
                f.write(script_content)
            
            print(f"\n✅ Scale tared successfully!")
            print(f"✅ Created tared_scale.py")
            print(f"✅ Run: python openscale-project/tared_scale.py")
            print(f"✅ Scale should now read 0g when empty!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    tare_scale()
