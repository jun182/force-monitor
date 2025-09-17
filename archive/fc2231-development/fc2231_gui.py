#!/usr/bin/env python3
"""
FC2231 Force Monitor - Kawaii GUI Interface
===========================================

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
import serial
import threading
import time
import statistics
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from collections import deque
from fc2231_calibration_manager import FC2231CalibrationManager

class FC2231KawaiiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 FC2231 Force Monitor ~ Kawaii Edition 🌸")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f8f5f0')
        
        # Serial connection parameters
        self.port = 'COM5'  # Arduino detected on COM5
        self.baudrate = 9600
        
        # Load calibration from persistent storage
        self.cal_manager = FC2231CalibrationManager()
        self.calibration_data = self.cal_manager.load_calibration()
        
        self.serial_connection = None
        self.reading_thread = None
        self.is_running = False
        
        # Data storage
        self.voltage_data = deque(maxlen=500)  # Store up to 500 points
        self.force_data = deque(maxlen=500)
        self.time_data = deque(maxlen=500)
        self.session_data = []
        
        # Current readings
        self.current_voltage = tk.StringVar(value="0.000 V")
        self.current_force_n = tk.StringVar(value="0.00 N")
        self.current_force_g = tk.StringVar(value="0.0 g")
        self.status_var = tk.StringVar(value="🔴 Status: Disconnected")
        
        # Statistics
        self.min_force = tk.StringVar(value="0.00 N")
        self.max_force = tk.StringVar(value="0.00 N")
        self.avg_force = tk.StringVar(value="0.00 N")
        self.reading_count = 0
        self.last_raw_voltage = 0.0
        
        # Calibration state
        self.calibrating = False
        self.calibration_readings = []
        
        # Drift monitoring
        self.baseline_force = None
        self.max_drift = 0.0
        self.drift_readings = []
        
        self.setup_gui()
        self.show_calibration_status()
        self.show_about_dialog()
        
    def setup_gui(self):
        """Setup the kawaii GUI interface"""
        # Title frame
        title_frame = tk.Frame(self.root, bg='#f8f5f0')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="🌸 FC2231 Force Monitor 🌸", 
                              font=('Arial', 20, 'bold'), 
                              bg='#f8f5f0', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Kawaii Arduino Force Sensor Interface", 
                                 font=('Arial', 12), 
                                 bg='#f8f5f0', fg='#7f8c8d')
        subtitle_label.pack()
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#f8f5f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Left panel for controls and readings
        left_panel = tk.Frame(main_frame, bg='#ecf0f1', relief='raised', bd=2)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # Current readings frame
        readings_frame = tk.LabelFrame(left_panel, text="📊 Current Readings", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#ecf0f1', fg='#2c3e50', 
                                      padx=10, pady=10)
        readings_frame.pack(pady=10, padx=10, fill='x')
        
        # Voltage display
        tk.Label(readings_frame, text="⚡ Voltage:", font=('Arial', 11, 'bold'),
                bg='#ecf0f1', fg='#8e44ad').pack(anchor='w')
        voltage_display = tk.Label(readings_frame, textvariable=self.current_voltage,
                                  font=('Courier', 14, 'bold'), 
                                  bg='#ecf0f1', fg='#27ae60')
        voltage_display.pack(anchor='w', pady=(0, 5))
        
        # Force N display - MAIN FOCUS
        tk.Label(readings_frame, text="💪 FORCE (Newtons):", font=('Arial', 13, 'bold'),
                bg='#ecf0f1', fg='#e67e22').pack(anchor='w')
        force_n_display = tk.Label(readings_frame, textvariable=self.current_force_n,
                                  font=('Courier', 18, 'bold'), 
                                  bg='#ecf0f1', fg='#c0392b')
        force_n_display.pack(anchor='w', pady=(0, 8))
        
        # Force g display
        tk.Label(readings_frame, text="⚖️ Force (Grams):", font=('Arial', 11, 'bold'),
                bg='#ecf0f1', fg='#3498db').pack(anchor='w')
        force_g_display = tk.Label(readings_frame, textvariable=self.current_force_g,
                                  font=('Courier', 14, 'bold'), 
                                  bg='#ecf0f1', fg='#2980b9')
        force_g_display.pack(anchor='w')
        
        # Drift monitoring frame
        drift_frame = tk.LabelFrame(left_panel, text="📊 Drift Monitor", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#ecf0f1', fg='#2c3e50',
                                   padx=10, pady=10)
        drift_frame.pack(pady=10, padx=10, fill='x')
        
        self.drift_status = tk.StringVar(value="No baseline set")
        drift_label = tk.Label(drift_frame, textvariable=self.drift_status,
                              font=('Arial', 10), bg='#ecf0f1', fg='#7f8c8d')
        drift_label.pack(anchor='w')
        
        # Control buttons frame
        control_frame = tk.LabelFrame(left_panel, text="🎮 Controls", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#ecf0f1', fg='#2c3e50',
                                     padx=10, pady=10)
        control_frame.pack(pady=10, padx=10, fill='x')
        
        # Start/Stop button
        self.start_button = tk.Button(control_frame, text="🟢 Start Reading", 
                                     command=self.start_reading,
                                     font=('Arial', 11, 'bold'), 
                                     bg='#27ae60', fg='white',
                                     padx=20, pady=8, relief='raised', bd=3)
        self.start_button.pack(fill='x', pady=2)
        
        self.stop_button = tk.Button(control_frame, text="🔴 Stop Reading", 
                                    command=self.stop_reading,
                                    font=('Arial', 11, 'bold'), 
                                    bg='#e74c3c', fg='white',
                                    padx=20, pady=8, relief='raised', bd=3,
                                    state='disabled')
        self.stop_button.pack(fill='x', pady=2)
        
        # Calibration buttons
        self.tare_button = tk.Button(control_frame, text="🎯 Quick Tare", 
                                    command=self.quick_tare,
                                    font=('Arial', 11), 
                                    bg='#9b59b6', fg='white',
                                    padx=15, pady=6, relief='raised', bd=2)
        self.tare_button.pack(fill='x', pady=2)
        
        # Drift monitoring button
        self.drift_button = tk.Button(control_frame, text="📊 Set Baseline for Drift", 
                                     command=self.set_drift_baseline,
                                     font=('Arial', 11), 
                                     bg='#3498db', fg='white',
                                     padx=15, pady=6, relief='raised', bd=2)
        self.drift_button.pack(fill='x', pady=2)
        
        self.calibrate_button = tk.Button(control_frame, text="⚖️ Calibrate Zero", 
                                         command=self.start_calibration,
                                         font=('Arial', 11), 
                                         bg='#f39c12', fg='white',
                                         padx=15, pady=6, relief='raised', bd=2)
        self.calibrate_button.pack(fill='x', pady=2)
        
        # Statistics frame
        stats_frame = tk.LabelFrame(left_panel, text="📈 Session Statistics", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#ecf0f1', fg='#2c3e50',
                                   padx=10, pady=10)
        stats_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(stats_frame, text="📉 Min:", font=('Arial', 10),
                bg='#ecf0f1', fg='#34495e').pack(anchor='w')
        tk.Label(stats_frame, textvariable=self.min_force,
                font=('Courier', 10, 'bold'), 
                bg='#ecf0f1', fg='#27ae60').pack(anchor='w', pady=(0, 3))
        
        tk.Label(stats_frame, text="📈 Max:", font=('Arial', 10),
                bg='#ecf0f1', fg='#34495e').pack(anchor='w')
        tk.Label(stats_frame, textvariable=self.max_force,
                font=('Courier', 10, 'bold'), 
                bg='#ecf0f1', fg='#e74c3c').pack(anchor='w', pady=(0, 3))
        
        tk.Label(stats_frame, text="📊 Avg:", font=('Arial', 10),
                bg='#ecf0f1', fg='#34495e').pack(anchor='w')
        tk.Label(stats_frame, textvariable=self.avg_force,
                font=('Courier', 10, 'bold'), 
                bg='#ecf0f1', fg='#3498db').pack(anchor='w')
        
        # Export buttons
        export_frame = tk.Frame(left_panel, bg='#ecf0f1')
        export_frame.pack(pady=10, padx=10, fill='x')
        
        self.export_button = tk.Button(export_frame, text="💾 Export Data", 
                                      command=self.export_data,
                                      font=('Arial', 10), 
                                      bg='#16a085', fg='white',
                                      padx=15, pady=6, relief='raised', bd=2)
        self.export_button.pack(fill='x', pady=2)
        
        self.about_button = tk.Button(export_frame, text="ℹ️ About", 
                                     command=self.show_about_dialog,
                                     font=('Arial', 10), 
                                     bg='#95a5a6', fg='white',
                                     padx=15, pady=6, relief='raised', bd=2)
        self.about_button.pack(fill='x', pady=2)
        
        # Right panel for graph
        right_panel = tk.Frame(main_frame, bg='#ecf0f1', relief='raised', bd=2)
        right_panel.pack(side='right', expand=True, fill='both')
        
        # Graph frame
        graph_frame = tk.LabelFrame(right_panel, text="📈 Real-time Force Graph", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#ecf0f1', fg='#2c3e50',
                                   padx=10, pady=10)
        graph_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create matplotlib figure - Focus on Force
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [1, 2]})
        self.fig.patch.set_facecolor('#ecf0f1')
        
        # Configure voltage plot (smaller)
        self.ax1.set_title('⚡ Voltage vs Time', fontsize=10, color='#2c3e50')
        self.ax1.set_ylabel('Voltage (V)', color='#8e44ad', fontsize=9)
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_facecolor('#f8f9fa')
        
        # Configure force plot (larger, main focus)
        self.ax2.set_title('💪 FORCE MONITOR - Real-time Force vs Time', fontsize=14, color='#2c3e50', weight='bold')
        self.ax2.set_xlabel('Time (seconds)', fontsize=11)
        self.ax2.set_ylabel('Force (N)', color='#e67e22', fontsize=12, weight='bold')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_facecolor('#f8f9fa')
        
        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill='both')
        
        # Status bar
        status_frame = tk.Frame(self.root, bg='#f8f5f0')
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                    font=('Arial', 10), 
                                    bg='#f8f5f0', fg='#e74c3c')
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Calibration status frame
        cal_frame = tk.Frame(self.root, bg='#f8f5f0')
        cal_frame.pack(pady=5)
        
        self.cal_status_var = tk.StringVar(value="Loading calibration...")
        self.cal_status_label = tk.Label(cal_frame, textvariable=self.cal_status_var,
                                        font=('Arial', 9), bg='#f8f5f0', fg='#7f8c8d')
        self.cal_status_label.pack()
    
    def show_calibration_status(self):
        """Display current calibration status"""
        status = self.cal_manager.get_calibration_status(self.calibration_data)
        tare_voltage = self.calibration_data.get("tare_voltage", 0.5)
        max_force = self.calibration_data.get("max_force_newtons", 100.0)
        self.cal_status_var.set(f"🔧 {status} | Tare: {tare_voltage:.3f}V | Max: {max_force:.0f}N")
    
    def start_reading(self):
        """Start reading from Arduino"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            
            self.is_running = True
            self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.reading_thread.start()
            
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_var.set("🟢 Status: Connected & Reading")
            self.status_label.config(fg='#27ae60')
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {self.port}:\n{e}")
            self.status_var.set(f"❌ Status: Connection Failed")
            self.status_label.config(fg='#e74c3c')
    
    def stop_reading(self):
        """Stop reading from Arduino"""
        self.is_running = False
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("🔴 Status: Disconnected")
        self.status_label.config(fg='#e74c3c')
    
    def read_serial_data(self):
        """Read data from Arduino in background thread"""
        start_time = time.time()
        
        while self.is_running and self.serial_connection:
            try:
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
                            self.last_raw_voltage = voltage
                            
                            # Apply our calibration
                            force_newtons = self.cal_manager.voltage_to_force(voltage, self.calibration_data)
                            force_grams = self.cal_manager.force_to_grams(force_newtons)
                            
                            # Store for drift monitoring
                            self.last_force_n = force_newtons
                            
                            # Update drift monitoring
                            self.update_drift_monitoring(force_newtons)
                            
                            # Store data for plotting
                            current_time = time.time() - start_time
                            self.voltage_data.append(voltage)
                            self.force_data.append(force_newtons)
                            self.time_data.append(current_time)
                            
                            # Handle calibration
                            if self.calibrating:
                                self.calibration_readings.append(voltage)
                                self.root.after(0, lambda: self.update_calibration_progress(len(self.calibration_readings)))
                                
                                if len(self.calibration_readings) >= 20:
                                    # Calculate new calibration
                                    try:
                                        new_calibration = self.cal_manager.perform_voltage_tare(self.calibration_readings)
                                        
                                        # Save calibration
                                        if self.cal_manager.save_calibration(new_calibration):
                                            self.calibration_data = new_calibration
                                            self.root.after(0, self.finish_calibration)
                                        else:
                                            self.root.after(0, lambda: self.calibration_error("Failed to save calibration"))
                                    except Exception as e:
                                        self.root.after(0, lambda: self.calibration_error(str(e)))
                            
                            # Update GUI
                            self.root.after(0, lambda: self.update_display(voltage, force_newtons, force_grams))
                            
                            # Store session data
                            self.session_data.append({
                                'timestamp': datetime.now(),
                                'voltage': voltage,
                                'force_n': force_newtons,
                                'force_g': force_grams
                            })
                            
                        except (ValueError, IndexError):
                            pass
                            
            except Exception as e:
                if self.is_running:  # Only show error if we're supposed to be running
                    print(f"Serial read error: {e}")
                break
    
    def update_display(self, voltage, force_n, force_g):
        """Update GUI display with new readings"""
        self.current_voltage.set(f"{voltage:.3f} V")
        self.current_force_n.set(f"{force_n:.2f} N")
        self.current_force_g.set(f"{force_g:.1f} g")
        
        self.reading_count += 1
        
        # Update statistics
        if len(self.force_data) > 0:
            forces = list(self.force_data)
            non_zero_forces = [f for f in forces if abs(f) > 0.01]  # >0.01N threshold
            
            if non_zero_forces:
                self.min_force.set(f"{min(non_zero_forces):.2f} N")
                self.max_force.set(f"{max(non_zero_forces):.2f} N")
                self.avg_force.set(f"{statistics.mean(non_zero_forces):.2f} N")
        
        # Update plot every 10 readings
        if self.reading_count % 10 == 0:
            self.update_plot()
    
    def update_plot(self):
        """Update the real-time plot"""
        if len(self.time_data) > 0:
            # Clear and plot voltage
            self.ax1.clear()
            self.ax1.plot(self.time_data, self.voltage_data, 'b-', linewidth=1.5, alpha=0.6)
            self.ax1.set_title('⚡ Voltage vs Time', fontsize=10, color='#2c3e50')
            self.ax1.set_ylabel('Voltage (V)', color='#8e44ad', fontsize=9)
            self.ax1.grid(True, alpha=0.3)
            self.ax1.set_facecolor('#f8f9fa')
            
            # Clear and plot force - MAIN FOCUS
            self.ax2.clear()
            self.ax2.plot(self.time_data, self.force_data, 'r-', linewidth=3, alpha=0.8)
            self.ax2.set_title('💪 FORCE MONITOR - Real-time Force vs Time', fontsize=14, color='#2c3e50', weight='bold')
            self.ax2.set_xlabel('Time (seconds)', fontsize=11)
            self.ax2.set_ylabel('Force (N)', color='#e67e22', fontsize=12, weight='bold')
            self.ax2.grid(True, alpha=0.3)
            self.ax2.set_facecolor('#f8f9fa')
            
            # Refresh canvas
            self.canvas.draw()
    
    def quick_tare(self):
        """Quick tare using current reading"""
        if hasattr(self, 'last_raw_voltage'):
            # Create calibration data with new tare
            new_calibration = self.calibration_data.copy()
            new_calibration["tare_voltage"] = self.last_raw_voltage
            
            # Save calibration
            if self.cal_manager.save_calibration(new_calibration):
                self.calibration_data = new_calibration
                self.show_calibration_status()
                self.status_label.config(text="🎯 Status: Quick Tare Applied", fg='#9b59b6')
                messagebox.showinfo("Tare Complete", 
                                  f"🎌 New tare voltage: {self.last_raw_voltage:.4f}V\n💾 Calibration saved!")
                # Reset back to connected after 2 seconds
                self.root.after(2000, lambda: self.status_label.config(text="🟢 Status: Connected & Reading", fg='#27ae60'))
            else:
                messagebox.showerror("Save Error", "Failed to save calibration!")
        else:
            messagebox.showwarning("No Data", "No reading available for tare!")
    
    def set_drift_baseline(self):
        """Set current force reading as baseline for drift monitoring"""
        if hasattr(self, 'last_force_n') and self.last_force_n is not None:
            self.baseline_force = self.last_force_n
            self.max_drift = 0.0
            self.drift_readings = []
            self.drift_status.set(f"Baseline: {self.baseline_force:.3f}N | Max drift: 0.000N")
            messagebox.showinfo("Drift Baseline Set", 
                              f"📊 Baseline force: {self.baseline_force:.3f}N\n"
                              f"Now unclamp the sensor to monitor drift!")
        else:
            messagebox.showwarning("No Data", "No force reading available!")
    
    def update_drift_monitoring(self, current_force):
        """Update drift monitoring with current force reading"""
        if self.baseline_force is not None:
            drift = abs(current_force - self.baseline_force)
            self.drift_readings.append(drift)
            
            # Keep only last 100 readings for average
            if len(self.drift_readings) > 100:
                self.drift_readings = self.drift_readings[-100:]
            
            # Update max drift
            if drift > self.max_drift:
                self.max_drift = drift
            
            # Calculate average drift
            avg_drift = sum(self.drift_readings) / len(self.drift_readings)
            
            # Update display with color coding
            if self.max_drift < 0.1:  # Less than 0.1N drift
                color = '#27ae60'  # Green
                status = "🟢 STABLE"
            elif self.max_drift < 0.5:  # Less than 0.5N drift
                color = '#f39c12'  # Orange
                status = "🟡 MODERATE"
            else:  # More than 0.5N drift
                color = '#e74c3c'  # Red
                status = "🔴 HIGH DRIFT"
            
            self.drift_status.set(f"{status} | Baseline: {self.baseline_force:.3f}N | "
                                f"Current drift: {drift:.3f}N | Max: {self.max_drift:.3f}N")
            
            # Change color of drift label
            for widget in self.drift_status.master.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(fg=color)
    
    def start_calibration(self):
        """Start 20-point calibration"""
        if not self.is_running:
            messagebox.showwarning("Not Connected", "Please start reading first!")
            return
        
        result = messagebox.askyesno("Calibration", 
                                   "🌸 Start Kawaii Calibration? 🌸\n\n" +
                                   "Make sure no force is applied to the sensor.\n" +
                                   "This will take 20 readings for accurate calibration.")
        
        if result:
            self.calibrating = True
            self.calibration_readings = []
            self.calibrate_button.config(state='disabled')
            self.status_label.config(text="⚖️ Status: Calibrating...", fg='#f39c12')
    
    def update_calibration_progress(self, count):
        """Update calibration progress"""
        self.status_label.config(text=f"⚖️ Status: Calibrating... {count}/20", fg='#f39c12')
    
    def finish_calibration(self):
        """Complete the calibration process"""
        self.calibrating = False
        new_tare = self.calibration_data["tare_voltage"]
        stability = statistics.stdev(self.calibration_readings)
        
        self.status_label.config(text="🌸 Status: Calibration Complete!", fg='#27ae60')
        self.calibrate_button.config(state='normal')
        self.show_calibration_status()
        
        messagebox.showinfo("Calibration Complete", 
                          f"🎌 Kawaii Calibration Successful! 🎌\n\n" +
                          f"New tare voltage: {new_tare:.4f}V\n" +
                          f"Standard deviation: {stability:.4f}V\n" +
                          f"💾 Calibration saved to file!")
        # Reset back to connected after 3 seconds
        self.root.after(3000, lambda: self.status_label.config(text="🟢 Status: Connected & Reading", fg='#27ae60'))
    
    def calibration_error(self, error_msg):
        """Handle calibration errors"""
        self.calibrating = False
        self.status_label.config(text="❌ Status: Calibration Failed", fg='#e74c3c')
        self.calibrate_button.config(state='normal')
        messagebox.showerror("Calibration Error", f"Calibration failed:\n{error_msg}")
        self.root.after(2000, lambda: self.status_label.config(text="🟢 Status: Connected & Reading", fg='#27ae60'))
    
    def export_data(self):
        """Export session data to CSV"""
        if not self.session_data:
            messagebox.showwarning("No Data", "No data to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save FC2231 Data",
            initialname=f"fc2231_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header with metadata
                    writer.writerow(['🌸 FC2231 Force Monitor Data Export 🌸'])
                    writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                    writer.writerow(['Author', 'Johnny Hamnesjö Olausson'])
                    writer.writerow(['Email', 'johnny.hamnesjo@chalmers.se'])
                    writer.writerow(['Institution', 'Chalmers University of Technology'])
                    writer.writerow(['Sensor', 'FC2231 Amplified Force Sensor'])
                    writer.writerow(['Arduino', 'Uno R3'])
                    writer.writerow([])
                    
                    # Calibration info
                    writer.writerow(['⚡ Tare Voltage (V)', f'{self.calibration_data.get("tare_voltage", 0.5):.4f}'])
                    writer.writerow(['💪 Max Force (N)', f'{self.calibration_data.get("max_force_newtons", 100.0):.1f}'])
                    cal_date = self.calibration_data.get("calibration_date", "Never")
                    writer.writerow(['📅 Calibration Date', cal_date])
                    writer.writerow([])
                    
                    # Data header
                    writer.writerow(['Timestamp', 'Voltage (V)', 'Force (N)', 'Force (g)'])
                    
                    # Data rows
                    for data_point in self.session_data:
                        writer.writerow([
                            data_point['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                            f"{data_point['voltage']:.4f}",
                            f"{data_point['force_n']:.3f}",
                            f"{data_point['force_g']:.1f}"
                        ])
                
                messagebox.showinfo("Export Complete", 
                                  f"🎌 Data exported successfully! 🎌\n\n" +
                                  f"File: {filename}\n" +
                                  f"Records: {len(self.session_data)}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data:\n{e}")
    
    def show_about_dialog(self):
        """Show about dialog"""
        about_text = """🌸 FC2231 Force Monitor ~ Kawaii Edition 🌸

Kawaii Arduino Force Sensor Interface

👨‍🔬 Author: Johnny Hamnesjö Olausson
📧 Email: johnny.hamnesjo@chalmers.se
🏛️ Institution: Chalmers University of Technology
📚 Department: Department of Industrial and Materials Science

🔌 Hardware: Arduino Uno R3 + FC2231 Sensor
💻 Software: Python + tkinter + matplotlib
📄 License: GNU General Public License v3.0

🌸 Features:
• Real-time force and voltage monitoring
• Persistent calibration system
• Live data plotting and export
• Kawaii interface design
• Professional accuracy

🎌 Designed with love and precision! 🎌
"""
        
        messagebox.showinfo("About FC2231 Monitor", about_text)

def main():
    """Main function to run the FC2231 GUI"""
    root = tk.Tk()
    app = FC2231KawaiiGUI(root)
    
    def on_closing():
        if app.is_running:
            app.stop_reading()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()