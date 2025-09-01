import serial
import time

PORT = 'COM4'
BAUDRATE = 9600

def analyze_raw_data():
    print("=== OpenScale Raw Data Analyzer ===")
    print("This will show EXACTLY what the OpenScale is sending")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
            print("Connected to OpenScale. Waiting for data...")
            print("Format: [Raw Bytes] -> [Decoded String] -> [Parsed Values]")
            print("-" * 60)
            
            line_count = 0
            while True:
                # Read raw bytes
                raw_line = ser.readline()
                
                if raw_line:
                    line_count += 1
                    
                    # Show raw bytes
                    raw_hex = raw_line.hex()
                    raw_ascii = raw_line
                    
                    # Try to decode
                    try:
                        decoded = raw_line.decode('utf-8', errors='replace').strip()
                    except:
                        decoded = "DECODE_ERROR"
                    
                    print(f"\nLine {line_count}:")
                    print(f"  RAW BYTES: {raw_hex}")
                    print(f"  RAW ASCII: {raw_ascii}")
                    print(f"  DECODED:   '{decoded}'")
                    
                    # Try to parse as CSV
                    if ',' in decoded:
                        parts = decoded.split(',')
                        print(f"  CSV PARTS: {parts}")
                        print(f"  PART COUNT: {len(parts)}")
                        
                        # Analyze each part
                        for i, part in enumerate(parts):
                            part_type = "unknown"
                            try:
                                if part.isdigit():
                                    part_type = "integer"
                                elif '.' in part and part.replace('.', '').replace('-', '').isdigit():
                                    part_type = "float"
                                elif part.replace('-', '').isdigit():
                                    part_type = "negative_integer"
                            except:
                                pass
                            
                            print(f"    Part[{i}]: '{part}' ({part_type})")
                    
                    # If it looks like weight data, analyze further
                    if ',' in decoded and len(decoded.split(',')) >= 2:
                        parts = decoded.split(',')
                        try:
                            if parts[0].isdigit() and len(parts) >= 2:
                                reading_num = int(parts[0])
                                weight_value = float(parts[1]) if parts[1].replace('.', '').replace('-', '').isdigit() else None
                                
                                if weight_value is not None:
                                    print(f"  WEIGHT ANALYSIS:")
                                    print(f"    Reading #: {reading_num}")
                                    print(f"    Weight value: {weight_value}")
                                    print(f"    Unit assumed: {parts[2] if len(parts) > 2 else 'unknown'}")
                                    
                                    # Show different unit interpretations
                                    print(f"    If pounds: {weight_value} lbs = {weight_value * 453.592:.1f} grams")
                                    print(f"    If kg: {weight_value} kg = {weight_value * 1000:.1f} grams")
                                    print(f"    If grams: {weight_value} grams")
                                    print(f"    If raw ADC: {weight_value} (needs calibration)")
                        except:
                            pass
                    
                    print("-" * 60)
                    
                    # Stop after 10 readings for analysis
                    if line_count >= 10:
                        print("\n🔍 ANALYSIS COMPLETE")
                        print("Based on the raw data above, what do you observe?")
                        print("1. What format is the data in?")
                        print("2. What units appear to be used?")
                        print("3. Do the numbers make sense for your setup?")
                        break
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n✅ Analysis stopped by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_raw_data()
