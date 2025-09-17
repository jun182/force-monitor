import serial
import time
from datetime import datetime

PORT = 'COM4'
BAUDRATE = 9600
TARE_POINT_GRAMS = -15901.7  # From previous tare

def monitor_drift():
    print("=== OpenScale Drift Monitor ===")
    print("Monitoring weight and temperature over time...")
    print("This will help identify why weight is increasing")
    print("Press Ctrl+C to stop and show graph")
    print("-" * 50)
    
    timestamps = []
    weights = []
    temperatures = []
    raw_readings = []
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            # Skip initial messages
            time.sleep(2)
            for _ in range(5):
                ser.readline()
            
            start_time = time.time()
            
            while True:
                line = ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and decoded.split(',')[0].isdigit():
                        parts = decoded.split(',')
                        if len(parts) >= 4:
                            current_time = time.time() - start_time
                            raw_lbs = float(parts[1])
                            temp = float(parts[3])
                            
                            # Convert to grams and subtract tare point
                            raw_grams = raw_lbs * 453.592
                            weight_grams = raw_grams - TARE_POINT_GRAMS
                            
                            # Store data
                            timestamps.append(current_time)
                            weights.append(weight_grams)
                            temperatures.append(temp)
                            raw_readings.append(raw_grams)
                            
                            print(f"Time: {current_time:6.1f}s | Weight: {weight_grams:7.1f}g | "
                                  f"Temp: {temp:6.2f}°C | Raw: {raw_grams:8.1f}g")
                
                time.sleep(0.5)  # Read every 500ms
                
    except KeyboardInterrupt:
        print(f"\n📊 Analysis of {len(weights)} readings over {timestamps[-1]:.1f} seconds:")
        
        if len(weights) > 2:
            # Calculate drift rates
            weight_start = weights[0]
            weight_end = weights[-1]
            weight_drift = weight_end - weight_start
            weight_drift_rate = weight_drift / timestamps[-1]  # g/s
            
            temp_start = temperatures[0]
            temp_end = temperatures[-1]
            temp_drift = temp_end - temp_start
            
            print(f"Weight drift: {weight_drift:+.1f}g total ({weight_drift_rate:+.2f}g/s)")
            print(f"Temperature drift: {temp_drift:+.3f}°C")
            print(f"Raw reading drift: {raw_readings[-1] - raw_readings[0]:+.1f}g")
            
            # Analyze the cause
            print(f"\n🔍 Drift Analysis:")
            if abs(weight_drift_rate) > 1:  # More than 1g/s drift
                print("❌ Significant drift detected!")
                if abs(temp_drift) > 0.5:
                    print("🌡️  Temperature change may be causing drift")
                if weight_drift_rate > 0:
                    print("📈 Upward drift suggests:")
                    print("   - Load cell creep")
                    print("   - Electronic drift")
                    print("   - Mounting stress")
                else:
                    print("📉 Downward drift suggests:")
                    print("   - Load cell relaxation")
                    print("   - Temperature compensation")
            else:
                print("✅ Drift is within acceptable range")
            
            # Save data to file
            with open('openscale-project/drift_data.csv', 'w') as f:
                f.write("Time(s),Weight(g),Temperature(C),RawReading(g)\n")
                for i in range(len(timestamps)):
                    f.write(f"{timestamps[i]:.1f},{weights[i]:.1f},{temperatures[i]:.2f},{raw_readings[i]:.1f}\n")
            
            print(f"💾 Data saved to drift_data.csv")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    monitor_drift()
