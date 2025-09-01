import serial
import time
import traceback

# Update this to match your OpenScale COM port (e.g., 'COM3')
PORT = 'COM4'
BAUDRATE = 9600

def read_openscale(port=PORT, baudrate=BAUDRATE):
    try:
        print(f"Attempting to open serial port {port} at {baudrate} baud...")
        with serial.Serial(port, baudrate, timeout=2) as ser:
            print(f"Connected to {port} at {baudrate} baud.")
            print("Sending newline to trigger OpenScale response...")
            ser.write(b'\r\n')
            time.sleep(0.5)
            print("Reading data from OpenScale. Press Ctrl+C to stop.")
            while True:
                try:
                    line = ser.readline()
                    if not line:
                        print("[Warning] No data received. Retrying...")
                        time.sleep(1)
                        continue
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if decoded:
                        # Parse and format OpenScale data for better readability
                        if ',' in decoded and decoded.split(',')[0].isdigit():
                            # This looks like sensor data: reading#,weight,unit,temp,status,
                            parts = decoded.split(',')
                            if len(parts) >= 5:
                                reading_num = parts[0]
                                weight = parts[1]
                                unit = parts[2]
                                temp = parts[3]
                                status = parts[4]
                                print(f"📊 Reading #{reading_num:>4} | Weight: {weight:>8} {unit:<3} | Temp: {temp:>6}°C | Status: {status}")
                            else:
                                print(f"[DATA] {decoded}")
                        else:
                            # This is status/info message, display as-is with timestamp
                            import datetime
                            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] {decoded}")
                except Exception as e:
                    print(f"[Error] Failed to read or decode line: {e}")
                    traceback.print_exc()
    except serial.SerialException as e:
        print(f"[SerialException] {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"[Exception] {e}")
        traceback.print_exc()
    except KeyboardInterrupt:
        print("\nStopped reading.")

if __name__ == "__main__":
    read_openscale()
