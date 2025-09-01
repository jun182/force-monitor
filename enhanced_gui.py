#!/usr/bin/env python3
"""
Force Monitor - Enhanced GUI
============================

Author: Johnny Hamnesjö Olausson
Email: johnny.hamnesjo@chalmers.se
Institution: Chalmers University of Technology
Department: Department of Industrial and Materials Science

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import threading
import time
import statistics
import csv
from datetime import datetime, timedelta
from collections import deque

class EnhancedForceMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 Force Monitor v2.0 - Kawaii Edition 🌸")
        self.root.geometry("820x680")
        self.root.configure(bg='#f8f5f0')
        
        # Serial connection parameters
        self.port = 'COM4'
        self.baudrate = 9600
        self.tare_offset = -33.9975  # From accurate calibration
        self.serial_connection = None
        self.reading_thread = None
        self.is_running = False
        
        # Data tracking
        self.current_weight = 0.0
        self.session_weights = []
        self.readings_buffer = deque(maxlen=10)  # For smoothing
        self.session_start_time = datetime.now()
        self.reading_count = 0
        self.last_raw_reading = 0.0
        
        # Statistics
        self.min_weight = float('inf')
        self.max_weight = float('-inf')
        self.weight_sum = 0.0
        
        # Calibration state
        self.calibrating = False
        self.calibration_readings = []
        
        self.setup_gui()
        self.show_about_dialog()
        
    def setup_gui(self):
        # Title with kawaii styling
        title_label = tk.Label(self.root, text="🌸 Force Monitor ~ Kawaii Edition 🌸", 
                              font=('Arial', 18, 'bold'), 
                              bg='#f8f5f0', fg='#2c3e50')
        title_label.pack(pady=8)
        
        # Subtitle with author info
        subtitle_label = tk.Label(self.root, text="⚖️ Precision Load Cell Interface ⚖️", 
                                font=('Arial', 10), 
                                bg='#f8f5f0', fg='#7f8c8d')
        subtitle_label.pack(pady=2)
        
        # Status frame with kawaii styling
        status_frame = tk.Frame(self.root, bg='#f8f5f0')
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="🔴 Status: Disconnected", 
                                   font=('Arial', 12), 
                                   bg='#f8f5f0', fg='#e74c3c')
        self.status_label.pack()
        
        # Main display frame with subtle border
        main_frame = tk.Frame(self.root, bg='#ffffff', relief='raised', bd=1)
        main_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Weight display with zen-like spacing
        weight_frame = tk.Frame(main_frame, bg='#ffffff')
        weight_frame.pack(pady=20)
        
        tk.Label(weight_frame, text="📏 Current Weight", 
                font=('Arial', 14), bg='#ffffff', fg='#34495e').pack()
        
        self.weight_var = tk.StringVar(value="0.0")
        self.weight_label = tk.Label(weight_frame, textvariable=self.weight_var,
                                   font=('Arial', 48, 'bold'), 
                                   bg='#ffffff', fg='#27ae60')
        self.weight_label.pack(pady=5)
        
        tk.Label(weight_frame, text="📊 grams", 
                font=('Arial', 14), bg='#ffffff', fg='#7f8c8d').pack()
        
        # Statistics frame with kawaii layout
        stats_frame = tk.LabelFrame(main_frame, text="📈 Session Statistics ~ UwU", 
                                   font=('Arial', 11, 'bold'), bg='#ffffff', fg='#34495e',
                                   relief='ridge', bd=1)
        stats_frame.pack(pady=15, padx=15, fill='x')
        
        # Statistics row with emoji indicators
        stats_row1 = tk.Frame(stats_frame, bg='#ffffff')
        stats_row1.pack(pady=8, fill='x')
        
        # Min weight
        min_frame = tk.Frame(stats_row1, bg='#ffffff')
        min_frame.pack(side='left', expand=True, fill='x')
        tk.Label(min_frame, text="📉 Minimum", font=('Arial', 9), bg='#ffffff', fg='#34495e').pack()
        self.min_var = tk.StringVar(value="--")
        tk.Label(min_frame, textvariable=self.min_var, font=('Arial', 13, 'bold'), 
                bg='#ffffff', fg='#3498db').pack()
        
        # Max weight
        max_frame = tk.Frame(stats_row1, bg='#ffffff')
        max_frame.pack(side='left', expand=True, fill='x')
        tk.Label(max_frame, text="📈 Maximum", font=('Arial', 9), bg='#ffffff', fg='#34495e').pack()
        self.max_var = tk.StringVar(value="--")
        tk.Label(max_frame, textvariable=self.max_var, font=('Arial', 13, 'bold'), 
                bg='#ffffff', fg='#e74c3c').pack()
        
        # Average weight
        avg_frame = tk.Frame(stats_row1, bg='#ffffff')
        avg_frame.pack(side='left', expand=True, fill='x')
        tk.Label(avg_frame, text="📊 Average", font=('Arial', 9), bg='#ffffff', fg='#34495e').pack()
        self.avg_var = tk.StringVar(value="--")
        tk.Label(avg_frame, textvariable=self.avg_var, font=('Arial', 13, 'bold'), 
                bg='#ffffff', fg='#9b59b6').pack()
        
        # Info frame with kawaii organization
        info_frame = tk.Frame(main_frame, bg='#ffffff')
        info_frame.pack(pady=12)
        
        # Temperature
        temp_frame = tk.Frame(info_frame, bg='#ffffff')
        temp_frame.pack(side='left', padx=25)
        
        tk.Label(temp_frame, text="🌡️ Temperature", 
                font=('Arial', 11), bg='#ffffff', fg='#34495e').pack()
        self.temp_var = tk.StringVar(value="--.-")
        tk.Label(temp_frame, textvariable=self.temp_var,
                font=('Arial', 16, 'bold'), bg='#ffffff', fg='#e67e22').pack()
        tk.Label(temp_frame, text="°C", 
                font=('Arial', 10), bg='#ffffff', fg='#7f8c8d').pack()
        
        # Reading count
        count_frame = tk.Frame(info_frame, bg='#ffffff')
        count_frame.pack(side='left', padx=25)
        
        tk.Label(count_frame, text="🔢 Readings", 
                font=('Arial', 11), bg='#ffffff', fg='#34495e').pack()
        self.count_var = tk.StringVar(value="0")
        tk.Label(count_frame, textvariable=self.count_var,
                font=('Arial', 16, 'bold'), bg='#ffffff', fg='#9b59b6').pack()
        
        # Session time
        time_frame = tk.Frame(info_frame, bg='#ffffff')
        time_frame.pack(side='right', padx=25)
        
        tk.Label(time_frame, text="⏱️ Session Time", 
                font=('Arial', 11), bg='#ffffff', fg='#34495e').pack()
        self.time_var = tk.StringVar(value="00:00")
        tk.Label(time_frame, textvariable=self.time_var,
                font=('Arial', 16, 'bold'), bg='#ffffff', fg='#16a085').pack()
        
        # Status indicators with kawaii dots
        indicator_frame = tk.Frame(main_frame, bg='#ffffff')
        indicator_frame.pack(pady=12)
        
        self.zero_indicator = tk.Label(indicator_frame, text="🔵", 
                                     font=('Arial', 16), bg='#ffffff')
        self.zero_indicator.pack(side='left', padx=15)
        tk.Label(indicator_frame, text="Zero", 
                font=('Arial', 10), bg='#ffffff', fg='#7f8c8d').pack(side='left')
        
        self.weight_indicator = tk.Label(indicator_frame, text="⚪", 
                                       font=('Arial', 16), bg='#ffffff')
        self.weight_indicator.pack(side='right', padx=15)
        tk.Label(indicator_frame, text="Weight Detected", 
                font=('Arial', 10), bg='#ffffff', fg='#7f8c8d').pack(side='right')
        
        # Control buttons frame 1 with kawaii styling
        button_frame1 = tk.Frame(self.root, bg='#f8f5f0')
        button_frame1.pack(pady=8)
        
        self.start_button = tk.Button(button_frame1, text="🎌 Start", 
                                    command=self.start_reading,
                                    font=('Arial', 11), 
                                    bg='#27ae60', fg='white',
                                    padx=18, pady=6, relief='raised', bd=2)
        self.start_button.pack(side='left', padx=4)
        
        self.stop_button = tk.Button(button_frame1, text="🛑 Stop", 
                                   command=self.stop_reading,
                                   font=('Arial', 11), 
                                   bg='#e74c3c', fg='white',
                                   padx=18, pady=6, state='disabled', relief='raised', bd=2)
        self.stop_button.pack(side='left', padx=4)
        
        self.reset_button = tk.Button(button_frame1, text="🔄 Reset Stats", 
                                     command=self.reset_statistics,
                                     font=('Arial', 11), 
                                     bg='#f39c12', fg='white',
                                     padx=15, pady=6, relief='raised', bd=2)
        self.reset_button.pack(side='left', padx=4)
        
        # Control buttons frame 2
        button_frame2 = tk.Frame(self.root, bg='#f8f5f0')
        button_frame2.pack(pady=5)
        
        self.calibrate_button = tk.Button(button_frame2, text="⚖️ Calibrate Zero", 
                                        command=self.start_calibration,
                                        font=('Arial', 11), 
                                        bg='#3498db', fg='white',
                                        padx=15, pady=6, relief='raised', bd=2)
        self.calibrate_button.pack(side='left', padx=4)
        
        self.tare_button = tk.Button(button_frame2, text="🎯 Quick Tare", 
                                   command=self.quick_tare,
                                   font=('Arial', 11), 
                                   bg='#9b59b6', fg='white',
                                   padx=15, pady=6, relief='raised', bd=2)
        self.tare_button.pack(side='left', padx=4)
        
        self.export_button = tk.Button(button_frame2, text="💾 Export Data", 
                                     command=self.export_data,
                                     font=('Arial', 11), 
                                     bg='#16a085', fg='white',
                                     padx=15, pady=6, relief='raised', bd=2)
        self.export_button.pack(side='left', padx=4)
        
        self.about_button = tk.Button(button_frame2, text="ℹ️ About", 
                                    command=self.show_about_dialog,
                                    font=('Arial', 11), 
                                    bg='#95a5a6', fg='white',
                                    padx=15, pady=6, relief='raised', bd=2)
        self.about_button.pack(side='left', padx=4)
        
        # Auto-start after a short delay
        self.root.after(1500, self.start_reading)
        self.root.after(1000, self.update_session_time)
        
    def start_reading(self):
        try:
            # Close any existing connection first
            if self.serial_connection:
                self.serial_connection.close()
                time.sleep(0.5)
                
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_running = True
            self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.reading_thread.start()
            
            # Reset session start time
            self.session_start_time = datetime.now()
            
            # Update UI with kawaii status
            self.status_label.config(text="🟢 Status: Connected & Reading", fg='#27ae60')
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
        except serial.SerialException as e:
            self.status_label.config(text=f"❌ Status: Serial Error - {str(e)}", fg='#e74c3c')
            messagebox.showerror("Connection Error", f"Failed to connect to {self.port}")
        except Exception as e:
            self.status_label.config(text=f"❌ Status: Error - {str(e)}", fg='#e74c3c')
    
    def stop_reading(self):
        self.is_running = False
        if self.serial_connection:
            self.serial_connection.close()
        
        # Update UI with kawaii status
        self.status_label.config(text="🔴 Status: Disconnected", fg='#e74c3c')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
    
    def start_calibration(self):
        """Start precise calibration process"""
        if not self.is_running:
            messagebox.showwarning("Not Connected", "Please start reading first!")
            return
            
        result = messagebox.askyesno("Calibration", 
                                   "🌸 Kawaii Calibration Process 🌸\n\n" +
                                   "Make sure the load cell is empty and stable.\n\n" +
                                   "This will take 20 readings to establish a new zero point.\n\n" +
                                   "Continue with calibration?")
        if result:
            self.calibrating = True
            self.calibration_readings = []
            self.status_label.config(text="🌸 Status: Calibrating... (0/20)", fg='#f39c12')
            self.calibrate_button.config(state='disabled')
    
    def quick_tare(self):
        """Quick tare using current reading"""
        if hasattr(self, 'last_raw_reading'):
            self.tare_offset = self.last_raw_reading
            self.status_label.config(text="🎯 Status: Quick Tare Applied", fg='#9b59b6')
            messagebox.showinfo("Tare Complete", 
                              f"🎌 New tare offset: {self.tare_offset:.2f}g")
            # Reset back to connected after 2 seconds
            self.root.after(2000, lambda: self.status_label.config(text="🟢 Status: Connected & Reading", fg='#27ae60'))
        else:
            messagebox.showwarning("No Data", "No reading available for tare!")
    
    def reset_statistics(self):
        """Reset all session statistics"""
        result = messagebox.askyesno("Reset Statistics", 
                                   "🔄 Reset all session statistics?")
        if result:
            self.session_weights = []
            self.min_weight = float('inf')
            self.max_weight = float('-inf')
            self.weight_sum = 0.0
            self.reading_count = 0
            self.session_start_time = datetime.now()
            
            # Update display
            self.min_var.set("--")
            self.max_var.set("--")
            self.avg_var.set("--")
            self.count_var.set("0")
            self.time_var.set("00:00")
    
    def show_about_dialog(self):
        """Show about dialog with author information"""
        about_text = """🌸 Force Monitor v2.0 🌸
Kawaii Precision Weight Measurement

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍🔬 Author:
Johnny Hamnesjö Olausson

📧 Email:
johnny.hamnesjo@chalmers.se

🏛️ Institution:
Chalmers University of Technology
Department of Industrial and Materials Science

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 License:
GNU General Public License v3.0

This program is free software: you can redistribute it 
and/or modify it under the terms of the GNU General 
Public License as published by the Free Software 
Foundation.

This program is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌸 Designed with kawaii simplicity and precision 🌸"""
        
        messagebox.showinfo("About", about_text)
    
    def export_data(self):
        """Export session data to CSV"""
        if not self.session_weights:
            messagebox.showwarning("No Data", "No data to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Session Data",
            initialvalue=f"force_monitor_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header with kawaii styling
                    writer.writerow(['🌸 Force Monitor Session Export 🌸', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                    writer.writerow([])
                    writer.writerow(['👨‍🔬 Author:', 'Johnny Hamnesjö Olausson'])
                    writer.writerow(['📧 Email:', 'johnny.hamnesjo@chalmers.se'])
                    writer.writerow(['🏛️ Institution:', 'Chalmers University of Technology'])
                    writer.writerow(['📚 Department:', 'Department of Industrial and Materials Science'])
                    writer.writerow([])
                    writer.writerow(['⚖️ Tare Offset (g)', f'{self.tare_offset:.4f}'])
                    writer.writerow(['🔢 Total Readings', len(self.session_weights)])
                    writer.writerow(['⏱️ Session Duration', self.time_var.get()])
                    writer.writerow([])  # Empty row
                    
                    # Write statistics with emojis
                    writer.writerow(['📊 Statistics'])
                    if self.session_weights:
                        writer.writerow(['📉 Minimum (g)', f'{min(self.session_weights):.2f}'])
                        writer.writerow(['📈 Maximum (g)', f'{max(self.session_weights):.2f}'])
                        writer.writerow(['📊 Average (g)', f'{statistics.mean(self.session_weights):.2f}'])
                        writer.writerow(['📏 Std Deviation (g)', f'{statistics.stdev(self.session_weights) if len(self.session_weights) > 1 else 0:.2f}'])
                    writer.writerow([])  # Empty row
                    
                    # Write data points
                    writer.writerow(['📋 Reading #', 'Weight (g)', 'Timestamp'])
                    for i, weight in enumerate(self.session_weights):
                        timestamp = (self.session_start_time + 
                                   timedelta(seconds=i*0.5)).strftime('%H:%M:%S')
                        writer.writerow([i+1, f'{weight:.2f}', timestamp])
                
                messagebox.showinfo("Export Complete", 
                                  f"🌸 Data exported successfully! 🌸\n\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", 
                                   f"Failed to export data:\n{str(e)}")
    
    def read_serial_data(self):
        # Skip initial messages
        time.sleep(1)
        for _ in range(10):
            if self.serial_connection:
                self.serial_connection.readline()
        
        while self.is_running and self.serial_connection:
            try:
                line = self.serial_connection.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and 'lbs' in decoded:
                        parts = decoded.split(',')
                        if len(parts) >= 4 and parts[2] == 'lbs':
                            raw_lbs = float(parts[1])
                            temp = float(parts[3])
                            
                            # Convert to grams and apply tare
                            raw_grams = raw_lbs * 453.592
                            self.last_raw_reading = raw_grams
                            weight_grams = raw_grams - self.tare_offset
                            
                            # Handle calibration with kawaii styling
                            if self.calibrating:
                                self.calibration_readings.append(raw_grams)
                                self.root.after(0, lambda: self.status_label.config(
                                    text=f"🌸 Status: Calibrating... ({len(self.calibration_readings)}/20)", 
                                    fg='#f39c12'))
                                
                                if len(self.calibration_readings) >= 20:
                                    # Calculate new tare offset
                                    new_offset = statistics.mean(self.calibration_readings)
                                    self.tare_offset = new_offset
                                    self.calibrating = False
                                    self.root.after(0, lambda: self.finish_calibration(new_offset))
                            
                            # Add to rolling buffer for smoothing
                            self.readings_buffer.append(weight_grams)
                            if len(self.readings_buffer) >= 3:
                                smoothed_weight = statistics.median(self.readings_buffer)
                            else:
                                smoothed_weight = weight_grams
                            
                            # Update GUI in main thread
                            self.root.after(0, self.update_display, smoothed_weight, temp)
                            
            except Exception as e:
                print(f"Error reading serial data: {e}")
                break
    
    def finish_calibration(self, new_offset):
        """Complete the calibration process"""
        self.status_label.config(text="🌸 Status: Calibration Complete!", fg='#27ae60')
        self.calibrate_button.config(state='normal')
        messagebox.showinfo("Calibration Complete", 
                          f"🎌 Kawaii Calibration Successful! 🎌\n\n" +
                          f"New calibration offset: {new_offset:.2f}g\n\n" +
                          f"Standard deviation: {statistics.stdev(self.calibration_readings):.2f}g")
        # Reset back to connected after 3 seconds
        self.root.after(3000, lambda: self.status_label.config(text="🟢 Status: Connected & Reading", fg='#27ae60'))
    
    def update_display(self, weight, temperature):
        # Update current weight display with Japanese-style indicators
        if abs(weight) < 5:  # Within 5g, show as zero
            self.weight_var.set("0.0")
            self.weight_label.config(fg='#27ae60')  # Green for zero
            self.zero_indicator.config(text="🟢")  # Green circle
            self.weight_indicator.config(text="⚪")  # White circle
            display_weight = 0.0
        else:
            self.weight_var.set(f"{weight:.1f}")
            if weight > 0:
                self.weight_label.config(fg='#e67e22')  # Orange for positive
                self.weight_indicator.config(text="🟠")  # Orange circle
            else:
                self.weight_label.config(fg='#3498db')  # Blue for negative
                self.weight_indicator.config(text="🔵")  # Blue circle
            self.zero_indicator.config(text="⚪")  # White circle
            display_weight = weight
        
        # Add to session data (only if not calibrating)
        if not self.calibrating:
            self.session_weights.append(display_weight)
            self.current_weight = display_weight
            
            # Update statistics
            if display_weight != 0:  # Don't include zero readings in min/max
                if display_weight < self.min_weight:
                    self.min_weight = display_weight
                if display_weight > self.max_weight:
                    self.max_weight = display_weight
            
            # Update statistics display
            if self.session_weights:
                non_zero_weights = [w for w in self.session_weights if abs(w) > 5]
                if non_zero_weights:
                    self.min_var.set(f"{min(non_zero_weights):.1f}g")
                    self.max_var.set(f"{max(non_zero_weights):.1f}g")
                    self.avg_var.set(f"{statistics.mean(non_zero_weights):.1f}g")
                else:
                    self.min_var.set("0.0g")
                    self.max_var.set("0.0g")
                    self.avg_var.set("0.0g")
        
        # Update temperature
        self.temp_var.set(f"{temperature:.1f}")
        
        # Update reading count
        if not self.calibrating:
            self.reading_count += 1
            self.count_var.set(str(self.reading_count))
    
    def update_session_time(self):
        """Update the session time display"""
        if hasattr(self, 'session_start_time'):
            elapsed = datetime.now() - self.session_start_time
            hours, remainder = divmod(elapsed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                time_str = f"{minutes:02d}:{seconds:02d}"
            self.time_var.set(time_str)
        
        # Schedule next update
        self.root.after(1000, self.update_session_time)
    
    def on_closing(self):
        self.stop_reading()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedForceMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
