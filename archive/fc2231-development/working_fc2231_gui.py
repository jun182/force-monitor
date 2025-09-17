#!/usr/bin/env python3
"""
💪 Fixed FC2231 Force Monitor GUI
Working version with proper threading and event handling
"""

import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time
import queue
from fc2231_calibration_manager import FC2231CalibrationManager

class WorkingFC2231GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💪 FC2231 Force Monitor - WORKING VERSION")
        self.root.geometry("500x400")
        self.root.configure(bg='#ecf0f1')
        
        # Make window stay on top temporarily
        self.root.attributes('-topmost', True)
        self.root.after(1000, lambda: self.root.attributes('-topmost', False))
        
        # Serial connection
        self.port = 'COM5'
        self.baudrate = 9600
        self.serial_connection = None
        self.is_running = False
        
        # Data queue for thread safety
        self.data_queue = queue.Queue()
        
        # Calibration
        self.cal_manager = FC2231CalibrationManager()
        self.calibration_data = self.cal_manager.load_calibration()
        
        # Current readings
        self.reading_count = 0
        self.current_voltage = 0.0
        self.current_force = 0.0
        
        self.setup_gui()
        self.start_gui_updater()
        
    def setup_gui(self):
        # Title
        title = tk.Label(self.root, text="💪 FC2231 Force Monitor", 
                        font=('Arial', 18, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=15)
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#ecf0f1')
        status_frame.pack(pady=10)
        
        self.status_var = tk.StringVar(value="⭕ Ready to Connect")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#7f8c8d')
        self.status_label.pack()
        
        # Readings frame
        readings_frame = tk.LabelFrame(self.root, text="📊 Live Readings", 
                                      font=('Arial', 14, 'bold'),
                                      bg='#ecf0f1', fg='#2c3e50',
                                      padx=20, pady=15)
        readings_frame.pack(pady=20, padx=20, fill='x')
        
        # Reading count
        self.count_var = tk.StringVar(value="Readings: 0")
        count_label = tk.Label(readings_frame, textvariable=self.count_var,
                              font=('Arial', 11), bg='#ecf0f1', fg='#7f8c8d')
        count_label.pack()
        
        # Voltage display
        tk.Label(readings_frame, text="⚡ Voltage:", font=('Arial', 12, 'bold'),
                bg='#ecf0f1', fg='#8e44ad').pack(anchor='w', pady=(10,0))
        self.voltage_var = tk.StringVar(value="0.000 V")
        voltage_display = tk.Label(readings_frame, textvariable=self.voltage_var,
                                  font=('Courier', 16, 'bold'), bg='#ecf0f1', fg='#9b59b6')
        voltage_display.pack(anchor='w')
        
        # Force display - MAIN FOCUS
        tk.Label(readings_frame, text="💪 FORCE:", font=('Arial', 14, 'bold'),
                bg='#ecf0f1', fg='#e67e22').pack(anchor='w', pady=(15,0))
        self.force_var = tk.StringVar(value="0.000 N")
        force_display = tk.Label(readings_frame, textvariable=self.force_var,
                                font=('Courier', 24, 'bold'), bg='#ecf0f1', fg='#e74c3c')
        force_display.pack(anchor='w')
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#ecf0f1')
        button_frame.pack(pady=30)
        
        # Start button with explicit binding
        self.start_button = tk.Button(button_frame, text="🟢 START READING", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#27ae60', fg='white', 
                                     width=15, height=2,
                                     relief='raised', bd=3)
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.start_button.bind('<Button-1>', self.on_start_click)
        
        # Stop button
        self.stop_button = tk.Button(button_frame, text="🔴 STOP READING", 
                                    font=('Arial', 14, 'bold'),
                                    bg='#e74c3c', fg='white', 
                                    width=15, height=2,
                                    relief='raised', bd=3,
                                    state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=10)
        self.stop_button.bind('<Button-1>', self.on_stop_click)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="Click START to begin reading from FC2231 sensor on COM5",
                               font=('Arial', 10), bg='#ecf0f1', fg='#7f8c8d')
        instructions.pack(pady=(20,10))
        
    def on_start_click(self, event):
        """Handle start button click with explicit event binding"""
        print("🔧 START button clicked via event binding!")
        self.start_reading()
        
    def on_stop_click(self, event):
        """Handle stop button click with explicit event binding"""
        print("🔧 STOP button clicked via event binding!")
        self.stop_reading()
        
    def start_reading(self):
        """Start reading from Arduino"""
        print("🔧 start_reading() function called")
        
        if self.is_running:
            print("🔧 Already running, ignoring")
            return
            
        try:
            print(f"🔧 Attempting to connect to {self.port} at {self.baudrate} baud...")
            self.status_var.set("🔌 Connecting...")
            self.root.update()  # Force GUI update
            
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            print("🔧 Serial connection established, waiting for Arduino...")
            time.sleep(2)  # Wait for Arduino initialization
            
            self.is_running = True
            self.reading_count = 0
            
            # Start reading thread
            self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.reading_thread.start()
            print("🔧 Reading thread started")
            
            # Update GUI
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_var.set("🟢 Connected & Reading")
            self.status_label.config(fg='#27ae60')
            
            print("✅ Successfully started reading!")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"❌ Exception type: {type(e).__name__}")
            self.status_var.set(f"❌ Failed: {str(e)[:30]}...")
            self.status_label.config(fg='#e74c3c')
            messagebox.showerror("Connection Error", f"Failed to connect to {self.port}:\n\n{e}")
            
    def stop_reading(self):
        """Stop reading from Arduino"""
        print("🔧 Stopping reading...")
        self.is_running = False
        
        if self.serial_connection:
            try:
                self.serial_connection.close()
                print("🔧 Serial connection closed")
            except:
                pass
                
        # Update GUI
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("⭕ Disconnected")
        self.status_label.config(fg='#7f8c8d')
        print("🔧 Reading stopped")
        
    def read_serial_data(self):
        """Read data from Arduino in background thread"""
        print("🔧 Serial reading thread started")
        
        while self.is_running and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline()
                    if line:
                        decoded = line.decode('utf-8', errors='ignore').strip()
                        
                        # Skip Arduino command responses
                        if decoded.startswith("FC2231,") or not ',' in decoded:
                            continue
                            
                        # Parse data line: reading,voltage,V,temp,force_N,N,force_g,g,timestamp
                        parts = decoded.split(',')
                        if len(parts) >= 9:
                            try:
                                voltage = float(parts[1])
                                force_newtons = self.cal_manager.voltage_to_force(voltage, self.calibration_data)
                                
                                # Put data in queue for GUI thread
                                self.data_queue.put({
                                    'voltage': voltage,
                                    'force': force_newtons,
                                    'timestamp': time.time()
                                })
                                
                                # Print every 20th reading
                                self.reading_count += 1
                                if self.reading_count % 20 == 0:
                                    print(f"📊 Reading #{self.reading_count}: {voltage:.3f}V → {force_newtons:.3f}N")
                                
                            except (ValueError, IndexError) as e:
                                print(f"⚠️ Parse error: {e}")
                                
                time.sleep(0.05)  # Small delay
                
            except Exception as e:
                if self.is_running:
                    print(f"❌ Reading error: {e}")
                break
                
        print("🔧 Serial reading thread ended")
        
    def start_gui_updater(self):
        """Start the GUI update loop"""
        self.update_gui()
        
    def update_gui(self):
        """Update GUI with new data from queue"""
        try:
            # Process all available data
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                self.current_voltage = data['voltage']
                self.current_force = data['force']
                
                # Update displays
                self.voltage_var.set(f"{self.current_voltage:.3f} V")
                self.force_var.set(f"{self.current_force:.3f} N")
                self.count_var.set(f"Readings: {self.reading_count}")
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"⚠️ GUI update error: {e}")
            
        # Schedule next update
        self.root.after(100, self.update_gui)  # Update every 100ms
        
    def run(self):
        """Run the GUI application"""
        print("💪 Starting Working FC2231 GUI...")
        print("🔧 Window should appear and be responsive")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("👋 GUI closed by user")
        finally:
            if self.is_running:
                self.stop_reading()

if __name__ == "__main__":
    app = WorkingFC2231GUI()
    app.run()