import serial
import time
import statistics

PORT = 'COM4'
BAUDRATE = 9600

def proper_tare_and_read():
    print("=== Proper OpenScale Tare & Read ===")
    print("Now that we understand the raw format, let's do this right!")
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            # Skip startup messages
            print("Connecting and skipping startup messages...")
            time.sleep(3)
            for _ in range(10):
                ser.readline()
            
            # Step 1: Establish zero point
            print("\n📍 STEP 1: Establishing Zero Point")
            print("Make sure load cell is clamped and NOTHING is on the free end")
            input("Press Enter when ready to tare...")
            
            print("Taking 20 readings for tare...")
            tare_readings = []
            
            for i in range(20):
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and 'lbs' in decoded:
                        parts = decoded.split(',')
                        if len(parts) >= 3 and parts[2] == 'lbs':
                            try:
                                weight_lbs = float(parts[1])
                                tare_readings.append(weight_lbs)
                                if i % 5 == 0:
                                    print(f"  Tare reading {i+1}/20: {weight_lbs} lbs")
                            except ValueError:
                                pass
                time.sleep(0.2)
            
            if not tare_readings:
                print("❌ No valid tare readings obtained")
                return
            
            tare_offset = statistics.mean(tare_readings)
            tare_stability = statistics.stdev(tare_readings)
            
            print(f"\n✅ Tare Complete:")
            print(f"   Offset: {tare_offset:.2f} lbs ({tare_offset * 453.592:.1f}g)")
            print(f"   Stability: ±{tare_stability:.3f} lbs (±{tare_stability * 453.592:.1f}g)")
            
            if tare_stability < 0.01:
                print("   🎯 Excellent stability!")
            elif tare_stability < 0.05:
                print("   ✅ Good stability")
            else:
                print("   ⚠️  Check mounting - readings are drifting")
            
            # Step 2: Live readings with tare applied
            print(f"\n📊 STEP 2: Live Weight Readings (Tared)")
            print("Add/remove weights to test accuracy")
            print("Press Ctrl+C to stop")
            print("-" * 50)
            print("Reading# |  Raw(lbs) | Tared(lbs) | Weight(g) | Temp(°C)")
            print("-" * 50)
            
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
                                temp = parts[3]
                                
                                # Apply tare
                                tared_lbs = raw_lbs - tare_offset
                                weight_grams = tared_lbs * 453.592
                                
                                # Format display
                                if abs(weight_grams) < 5:  # Less than 5g = essentially zero
                                    display = f"{reading_num:>7} | {raw_lbs:>8.2f} | {tared_lbs:>9.2f} | {'ZERO':>8} | {temp:>7}"
                                else:
                                    display = f"{reading_num:>7} | {raw_lbs:>8.2f} | {tared_lbs:>9.2f} | {weight_grams:>7.1f}g | {temp:>7}"
                                
                                print(display)
                                
                            except (ValueError, IndexError):
                                pass
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print(f"\n\n✅ Session Complete!")
        print(f"Your tare offset was: {tare_offset:.4f} lbs")
        print(f"Use this value for future accurate readings.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_known_weights():
    """Test with known weights to verify accuracy"""
    print("\n🧪 ACCURACY TEST")
    print("Do you have any objects with known weights to test?")
    print("Examples: coins (penny≈2.5g, nickel≈5g, quarter≈5.67g)")
    print("        : phone, wallet, keys (weigh on kitchen scale first)")
    
    response = input("Do you want to test with known weights? (y/n): ")
    if response.lower() == 'y':
        print("Great! After the tare, place your known weight and observe the reading.")
        print("This will tell us if our pound-to-gram conversion is accurate.")

if __name__ == "__main__":
    proper_tare_and_read()
    test_known_weights()
