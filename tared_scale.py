import serial
import time

PORT = 'COM4'
BAUDRATE = 9600

# Tared zero point
TARE_POINT_GRAMS = -15162.975771

def tared_readings():
    print("=== OpenScale - Tared to Zero ===")
    print(f"Zero point: {TARE_POINT_GRAMS:.1f} grams")
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
                            
                            print(f"{status} | #{reading_num:>4} | {display_weight:>8.1f}g | {temp:>6}°C")
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n✅ Stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    tared_readings()