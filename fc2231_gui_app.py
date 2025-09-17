#!/usr/bin/env python3
"""
FC2231 Force Monitor - Kawaii GUI Application
============================================

Author: Johnny Hamnesjö Olausson
Email: johnny.hamnesjo@chalmers.se
Institution: Chalmers University of Technology
Department: Department of Industrial and Materials Science

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import serial
import serial.tools.list_ports
import threading
import time
import csv
from datetime import datetime
from collections import deque
import queue
import statistics
from fc2231_calibration_manager import FC2231CalibrationManager

class FC2231GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 FC2231 Force Monitor - Kawaii Edition 🌸")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.cal_manager = FC2231CalibrationManager()
        self.calibration_data = self.cal_manager.load_calibration()
        
        # Data storage
        self.force_data = deque(maxlen=1000)  # Last 1000 readings
        self.time_data = deque(maxlen=1000)
        self.voltage_data = deque(maxlen=1000)
        self.session_forces = []
        self.session_start_time = datetime.now()
        
        # Connection and threading
        self.serial_connection = None
        self.data_thread = None
        self.running = False
        self.data_queue = queue.Queue()
        
        # Display settings
        self.display_interval = 5.0  # Default 5 seconds
        self.last_display_time = 0
        
        # CSV export
        self.export_data = []
        self.export_enabled = False
        
        # Statistics
        self.reading_count = 0
        
        # Create GUI
        self.create_widgets()
        self.setup_plot()
        
        # Start GUI update timer
        self.root.after(100, self.update_gui)
        
    def create_widgets(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # === LEFT PANEL - Controls ===
        control_frame = ttk.LabelFrame(main_frame, text="🎮 Controls", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Connection controls
        conn_frame = ttk.LabelFrame(control_frame, text="📡 Connection")
        conn_frame.pack(fill="x", pady=(0, 10))
        
        self.connect_btn = ttk.Button(conn_frame, text="🔍 Connect Arduino", command=self.connect_arduino)
        self.connect_btn.pack(pady=5)
        
        self.disconnect_btn = ttk.Button(conn_frame, text="❌ Disconnect", command=self.disconnect_arduino, state="disabled")
        self.disconnect_btn.pack(pady=5)
        
        self.status_label = ttk.Label(conn_frame, text="Status: Disconnected", foreground="red")
        self.status_label.pack(pady=5)
        
        # Calibration controls
        cal_frame = ttk.LabelFrame(control_frame, text="🌸 Calibration")
        cal_frame.pack(fill="x", pady=(0, 10))
        
        self.calibrate_btn = ttk.Button(cal_frame, text="🎌 Tare (Zero)", command=self.calibrate_sensor, state="disabled")
        self.calibrate_btn.pack(pady=5)
        
        self.cal_status_label = ttk.Label(cal_frame, text="Calibration: Not loaded")
        self.cal_status_label.pack(pady=5)
        
        # Display interval controls
        interval_frame = ttk.LabelFrame(control_frame, text="⏰ Display Interval")
        interval_frame.pack(fill="x", pady=(0, 10))
        
        self.interval_var = tk.DoubleVar(value=5.0)
        self.interval_scale = ttk.Scale(interval_frame, from_=0, to=10, orient="horizontal", 
                                       variable=self.interval_var, command=self.update_interval)
        self.interval_scale.pack(fill="x", pady=5)
        
        self.interval_label = ttk.Label(interval_frame, text="Interval: 5.0s")
        self.interval_label.pack(pady=5)
        
        # CSV Export controls
        export_frame = ttk.LabelFrame(control_frame, text="📊 CSV Export")
        export_frame.pack(fill="x", pady=(0, 10))
        
        self.export_var = tk.BooleanVar()
        self.export_check = ttk.Checkbutton(export_frame, text="📝 Record Data", 
                                           variable=self.export_var, command=self.toggle_export)
        self.export_check.pack(pady=5)
        
        self.export_btn = ttk.Button(export_frame, text="💾 Save CSV", command=self.save_csv)
        self.export_btn.pack(pady=5)
        
        self.export_status = ttk.Label(export_frame, text="Not recording")
        self.export_status.pack(pady=5)
        
        # === TOP RIGHT - Current Reading Display ===
        reading_frame = ttk.LabelFrame(main_frame, text="🌸 Current Reading", padding="10")
        reading_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Large display for current values
        self.force_display = ttk.Label(reading_frame, text="0.00 N", font=("Arial", 24, "bold"))
        self.force_display.pack(pady=10)
        
        self.force_grams_display = ttk.Label(reading_frame, text="0.0 g", font=("Arial", 16))
        self.force_grams_display.pack(pady=5)
        
        self.voltage_display = ttk.Label(reading_frame, text="Voltage: 0.000 V", font=("Arial", 12))
        self.voltage_display.pack(pady=5)
        
        self.temp_display = ttk.Label(reading_frame, text="Temp: 0.0°C", font=("Arial", 12))
        self.temp_display.pack(pady=5)
        
        self.reading_count_display = ttk.Label(reading_frame, text="Readings: 0", font=("Arial", 10))
        self.reading_count_display.pack(pady=5)
        
        # === BOTTOM RIGHT - Plot ===
        plot_frame = ttk.LabelFrame(main_frame, text="📈 Force vs Time", padding="5")
        plot_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Matplotlib will be embedded here
        self.plot_frame = plot_frame
        
        # === BOTTOM LEFT - Statistics ===
        stats_frame = ttk.LabelFrame(control_frame, text="📊 Session Statistics")
        stats_frame.pack(fill="both", expand=True)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=30, font=("Courier", 9))
        self.stats_text.pack(fill="both", expand=True)
        
        # Update calibration display
        self.update_calibration_display()
        
    def setup_plot(self):
        """Setup matplotlib plot"""
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.ax.set_title("🌸 Force Readings Over Time 🌸")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Force (N)")
        self.ax.grid(True, alpha=0.3)
        
        # Create empty line
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)
        
        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def find_arduino_port(self):
        """Auto-detect Arduino port"""
        available_ports = serial.tools.list_ports.comports()
        
        if not available_ports:
            return None
        
        # Try each port
        for port in available_ports:
            try:
                with serial.Serial(port.device, 9600, timeout=3) as ser:
                    time.sleep(2)  # Give Arduino time to initialize
                    ser.flushInput()
                    time.sleep(0.5)
                    
                    # Try to read some data
                    for attempt in range(5):
                        try:
                            line = ser.readline()
                            if line:
                                decoded = line.decode('utf-8', errors='ignore').strip()
                                if ',' in decoded and len(decoded.split(',')) >= 2:
                                    return port.device
                        except:
                            pass
                        time.sleep(0.5)
                        
            except serial.SerialException:
                continue
            except Exception:
                continue
        
        return None
        
    def connect_arduino(self):
        """Connect to Arduino"""
        if self.running:
            return
            
        port = self.find_arduino_port()
        if not port:
            messagebox.showerror("Connection Error", 
                               "No Arduino detected!\n\n" +
                               "Please check:\n" +
                               "• Arduino is connected via USB\n" +
                               "• Arduino has the FC2231 sketch uploaded\n" +
                               "• USB drivers are installed")
            return
        
        try:
            self.serial_connection = serial.Serial(port, 9600, timeout=2)
            time.sleep(3)  # Arduino startup time
            
            # Start data reading thread
            self.running = True
            self.data_thread = threading.Thread(target=self.read_data_thread, daemon=True)
            self.data_thread.start()
            
            # Update UI
            self.status_label.config(text=f"Status: Connected to {port}", foreground="green")
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.calibrate_btn.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {port}:\n{e}")
            
    def disconnect_arduino(self):
        """Disconnect from Arduino"""
        self.running = False
        
        if self.data_thread:
            self.data_thread.join(timeout=2)
            
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
            
        # Update UI
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.calibrate_btn.config(state="disabled")
        
    def read_data_thread(self):
        """Background thread to read data from Arduino"""
        while self.running and self.serial_connection:
            try:
                line = self.serial_connection.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and not decoded.startswith("FC2231,"):
                        self.data_queue.put(decoded)
                        
            except Exception as e:
                if self.running:  # Only show error if we're supposed to be running
                    self.data_queue.put(f"ERROR:{e}")
                break
                
    def process_data_line(self, line):
        """Process a data line from Arduino"""
        try:
            parts = line.strip().split(',')
            if len(parts) >= 9:
                reading_num = parts[0]
                voltage = float(parts[1])
                temp = float(parts[3])
                
                # Apply calibration
                force_n = self.cal_manager.voltage_to_force(voltage)
                force_g = self.cal_manager.force_to_grams(force_n)
                
                # Store data
                current_time = time.time()
                self.force_data.append(force_n)
                self.voltage_data.append(voltage)
                self.time_data.append(current_time)
                self.session_forces.append(force_n)
                self.reading_count += 1
                
                # Store for CSV export
                if self.export_enabled:
                    self.export_data.append({
                        'Reading': reading_num,
                        'DateTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        'Time': datetime.now().strftime("%H:%M:%S"),
                        'Voltage(V)': voltage,
                        'Force(N)': force_n,
                        'Force(g)': force_g,
                        'Temperature(°C)': temp
                    })
                
                # Update display values
                self.current_force = force_n
                self.current_force_g = force_g
                self.current_voltage = voltage
                self.current_temp = temp
                
                return True
                
        except (ValueError, IndexError):
            pass
            
        return False
        
    def update_gui(self):
        """Update GUI with new data"""
        # Process queued data
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                if data.startswith("ERROR:"):
                    messagebox.showerror("Serial Error", data[6:])
                    self.disconnect_arduino()
                else:
                    self.process_data_line(data)
            except queue.Empty:
                break
                
        # Update displays if we have current data
        if hasattr(self, 'current_force'):
            self.force_display.config(text=f"{self.current_force:.2f} N")
            self.force_grams_display.config(text=f"{self.current_force_g:.1f} g")
            self.voltage_display.config(text=f"Voltage: {self.current_voltage:.3f} V")
            self.temp_display.config(text=f"Temp: {self.current_temp:.1f}°C")
            self.reading_count_display.config(text=f"Readings: {self.reading_count}")
            
        # Update plot
        self.update_plot()
        
        # Update statistics
        self.update_statistics()
        
        # Schedule next update
        self.root.after(100, self.update_gui)
        
    def update_plot(self):
        """Update the real-time plot"""
        if len(self.time_data) > 1:
            # Convert absolute times to relative times in seconds
            start_time = self.time_data[0]
            relative_times = [(t - start_time) for t in self.time_data]
            
            self.line.set_data(relative_times, list(self.force_data))
            
            # Auto-scale axes
            self.ax.relim()
            self.ax.autoscale_view()
            
            # Redraw
            self.canvas.draw_idle()
            
    def update_statistics(self):
        """Update statistics display"""
        if self.session_forces:
            non_zero_forces = [f for f in self.session_forces if abs(f) > 0.05]
            if non_zero_forces:
                stats_text = "🌸 Session Stats 🌸\n\n"
                stats_text += f"📊 Count: {len(non_zero_forces)}\n"
                stats_text += f"📉 Min: {min(non_zero_forces):.2f}N\n"
                stats_text += f"📈 Max: {max(non_zero_forces):.2f}N\n"
                stats_text += f"📊 Avg: {statistics.mean(non_zero_forces):.2f}N\n"
                
                if len(non_zero_forces) > 1:
                    stats_text += f"📏 StdDev: {statistics.stdev(non_zero_forces):.2f}N\n"
                
                # Session duration
                duration = datetime.now() - self.session_start_time
                minutes, seconds = divmod(duration.seconds, 60)
                stats_text += f"⏱️ Duration: {minutes}:{seconds:02d}\n"
                
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(1.0, stats_text)
                
    def update_calibration_display(self):
        """Update calibration status display"""
        if self.calibration_data['calibration_date'] is not None:
            status = "✅ Calibrated"
            tare_v = self.calibration_data['tare_voltage']
            max_force = self.calibration_data['max_force_newtons']
            self.cal_status_label.config(text=f"{status}\nTare: {tare_v:.4f}V\nMax: {max_force:.1f}N")
        else:
            self.cal_status_label.config(text="❌ Not Calibrated\nPress Tare to calibrate")
            
    def update_interval(self, value):
        """Update display interval from scale"""
        self.display_interval = float(value)
        if self.display_interval == 0:
            self.interval_label.config(text="Interval: Real-time")
        else:
            self.interval_label.config(text=f"Interval: {self.display_interval:.1f}s")
            
    def toggle_export(self):
        """Toggle CSV export recording"""
        self.export_enabled = self.export_var.get()
        if self.export_enabled:
            self.export_data = []  # Clear previous data
            self.export_status.config(text="🔴 Recording...")
        else:
            self.export_status.config(text="Not recording")
            
    def save_csv(self):
        """Save recorded data to CSV file"""
        if not self.export_data:
            messagebox.showwarning("No Data", "No data recorded for export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV Export"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as csvfile:
                    fieldnames = ['Reading', 'DateTime', 'Time', 'Voltage(V)', 
                                'Force(N)', 'Force(g)', 'Temperature(°C)']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in self.export_data:
                        writer.writerow(row)
                        
                messagebox.showinfo("Export Complete", 
                                  f"Successfully exported {len(self.export_data)} readings to:\n{filename}")
                                  
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save file:\n{e}")
                
    def calibrate_sensor(self):
        """Perform sensor calibration"""
        if not self.serial_connection:
            messagebox.showerror("Error", "Not connected to Arduino!")
            return
            
        response = messagebox.askyesno("Calibration", 
                                     "Tare Calibration\n\n" +
                                     "Make sure no force is applied to the sensor!\n" +
                                     "Arduino will take 20 readings for calibration.\n\n" +
                                     "Continue with calibration?")
        
        if not response:
            return
            
        try:
            # Send tare command to Arduino
            self.serial_connection.write(b"TARE\n")
            time.sleep(0.1)
            
            # Wait for completion
            messagebox.showinfo("Calibrating", "Calibration in progress...\nThis will take a few seconds.")
            
            # The calibration will be handled by the Arduino
            # We just need to reload the calibration data after it's done
            self.root.after(3000, self.reload_calibration)  # Reload after 3 seconds
            
        except Exception as e:
            messagebox.showerror("Calibration Error", f"Failed to calibrate:\n{e}")
            
    def reload_calibration(self):
        """Reload calibration data after calibration"""
        self.calibration_data = self.cal_manager.load_calibration()
        self.update_calibration_display()
        messagebox.showinfo("Calibration Complete", "Sensor has been calibrated successfully!")

def main():
    root = tk.Tk()
    app = FC2231GUI(root)
    
    # Handle window close
    def on_closing():
        app.disconnect_arduino()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()