#!/usr/bin/env python3
"""
🎯 Simple FC2231 GUI Test
Minimal version to test basic functionality
"""

import tkinter as tk
import serial
import threading
import time
from fc2231_calibration_manager import FC2231CalibrationManager

class SimpleFC2231GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Simple FC2231 Test")
        self.root.geometry("400x300")
        self.root.configure(bg='#ecf0f1')
        
        # Serial connection
        self.port = 'COM5'
        self.baudrate = 9600
        self.serial_connection = None
        self.is_running = False
        
        # Calibration
        self.cal_manager = FC2231CalibrationManager()
        self.calibration_data = self.cal_manager.load_calibration()
        
        # Data
        self.last_voltage = 0.0
        self.last_force = 0.0
        self.reading_count = 0
        
        self.setup_gui()
        
    def setup_gui(self):
        # Title
        title = tk.Label(self.root, text="🎯 Simple FC2231 Test", 
                        font=('Arial', 16, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="⭕ Not Connected")
        status_label = tk.Label(self.root, textvariable=self.status_var,
                               font=('Arial', 12), bg='#ecf0f1', fg='#e74c3c')
        status_label.pack(pady=5)
        
        # Readings frame
        readings_frame = tk.Frame(self.root, bg='#ecf0f1')
        readings_frame.pack(pady=20)
        
        # Reading count
        self.count_var = tk.StringVar(value="Readings: 0")
        count_label = tk.Label(readings_frame, textvariable=self.count_var,
                              font=('Arial', 11), bg='#ecf0f1', fg='#7f8c8d')
        count_label.pack()
        
        # Voltage display
        self.voltage_var = tk.StringVar(value="Voltage: 0.000 V")
        voltage_label = tk.Label(readings_frame, textvariable=self.voltage_var,
                                font=('Courier', 14, 'bold'), bg='#ecf0f1', fg='#8e44ad')
        voltage_label.pack(pady=5)
        
        # Force display
        self.force_var = tk.StringVar(value="FORCE: 0.000 N")
        force_label = tk.Label(readings_frame, textvariable=self.force_var,
                              font=('Courier', 18, 'bold'), bg='#ecf0f1', fg='#e67e22')
        force_label.pack(pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#ecf0f1')
        button_frame.pack(pady=20)
        
        # Start button
        self.start_button = tk.Button(button_frame, text="🟢 START", 
                                     command=self.start_reading,
                                     font=('Arial', 12, 'bold'),
                                     bg='#27ae60', fg='white', width=10)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_button = tk.Button(button_frame, text="🔴 STOP", 
                                    command=self.stop_reading,
                                    font=('Arial', 12, 'bold'),
                                    bg='#e74c3c', fg='white', width=10,
                                    state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
    def start_reading(self):
        """Start reading from Arduino"""
        print("🔧 START button clicked!")  # Immediate debug output
        try:
            print(f"🔧 Attempting to connect to {self.port}...")
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            print("🔧 Serial connection created, waiting 2 seconds...")
            time.sleep(2)  # Wait for Arduino
            
            self.is_running = True
            self.reading_thread = threading.Thread(target=self.read_data, daemon=True)
            self.reading_thread.start()
            
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_var.set("🟢 Connected & Reading")
            print("✅ Connected successfully!")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"❌ Exception type: {type(e).__name__}")
            print(f"❌ Exception details: {str(e)}")
            self.status_var.set(f"❌ Connection Failed: {e}")
            # Re-enable start button if connection failed
            self.start_button.config(state='normal')
            
    def stop_reading(self):
        """Stop reading"""
        self.is_running = False
        if self.serial_connection:
            self.serial_connection.close()
            
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("⭕ Disconnected")
        print("🔴 Disconnected")
        
    def read_data(self):
        """Read data from Arduino"""
        print("🔧 Reading thread started")
        
        while self.is_running and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline()
                    if line:
                        decoded = line.decode('utf-8', errors='ignore').strip()
                        
                        # Skip command responses
                        if decoded.startswith("FC2231,") or not ',' in decoded:
                            continue
                            
                        # Parse: reading,voltage,V,temp,force_N,N,force_g,g,timestamp
                        parts = decoded.split(',')
                        if len(parts) >= 9:
                            try:
                                voltage = float(parts[1])
                                
                                # Apply calibration
                                force_newtons = self.cal_manager.voltage_to_force(voltage, self.calibration_data)
                                
                                # Update counts
                                self.reading_count += 1
                                self.last_voltage = voltage
                                self.last_force = force_newtons
                                
                                # Update GUI on main thread
                                self.root.after(0, self.update_display)
                                
                                # Print to console for debugging
                                if self.reading_count % 10 == 0:  # Every 10th reading
                                    print(f"📊 Reading #{self.reading_count}: {voltage:.3f}V → {force_newtons:.3f}N")
                                
                            except (ValueError, IndexError) as e:
                                print(f"⚠️ Parse error: {e} in line: {decoded}")
                                
                time.sleep(0.05)  # Small delay
                
            except Exception as e:
                if self.is_running:  # Only print if we're supposed to be running
                    print(f"❌ Reading error: {e}")
                break
                
        print("🔧 Reading thread stopped")
        
    def update_display(self):
        """Update the GUI display"""
        self.count_var.set(f"Readings: {self.reading_count}")
        self.voltage_var.set(f"Voltage: {self.last_voltage:.3f} V")
        self.force_var.set(f"FORCE: {self.last_force:.3f} N")
        
    def run(self):
        """Run the GUI"""
        try:
            print("🎯 Starting Simple FC2231 GUI...")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("👋 GUI closed by user")
        finally:
            if self.is_running:
                self.stop_reading()

if __name__ == "__main__":
    app = SimpleFC2231GUI()
    app.run()