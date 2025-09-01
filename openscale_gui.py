import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import threading
import time
import statistics
import csv
from datetime import datetime
from collections import deque
from datetime import datetime

class OpenScaleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SparkFun OpenScale Monitor")
        self.root.geometry("600x400")
        self.root.configure(bg='#f0f0f0')
        
        # Serial connection parameters
        self.port = 'COM4'
        self.baudrate = 9600
        self.tare_point = -15163.0  # From previous tare
        self.serial_connection = None
        self.reading_thread = None
        self.is_running = False
        
        self.setup_gui()
        
    def setup_gui(self):
        # Title
        title_label = tk.Label(self.root, text="SparkFun OpenScale", 
                              font=('Arial', 20, 'bold'), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#f0f0f0')
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: Disconnected", 
                                   font=('Arial', 12), 
                                   bg='#f0f0f0', fg='#e74c3c')
        self.status_label.pack()
        
        # Main display frame
        main_frame = tk.Frame(self.root, bg='white', relief='raised', bd=2)
        main_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Weight display
        weight_frame = tk.Frame(main_frame, bg='white')
        weight_frame.pack(pady=20)
        
        tk.Label(weight_frame, text="Weight", 
                font=('Arial', 16), bg='white', fg='#34495e').pack()
        
        self.weight_var = tk.StringVar(value="0.0")
        self.weight_label = tk.Label(weight_frame, textvariable=self.weight_var,
                                   font=('Arial', 36, 'bold'), 
                                   bg='white', fg='#27ae60')
        self.weight_label.pack()
        
        tk.Label(weight_frame, text="grams", 
                font=('Arial', 14), bg='white', fg='#7f8c8d').pack()
        
        # Info frame
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(pady=10)
        
        # Temperature
        temp_frame = tk.Frame(info_frame, bg='white')
        temp_frame.pack(side='left', padx=20)
        
        tk.Label(temp_frame, text="Temperature", 
                font=('Arial', 12), bg='white', fg='#34495e').pack()
        self.temp_var = tk.StringVar(value="--.-")
        tk.Label(temp_frame, textvariable=self.temp_var,
                font=('Arial', 18, 'bold'), bg='white', fg='#e67e22').pack()
        tk.Label(temp_frame, text="°C", 
                font=('Arial', 10), bg='white', fg='#7f8c8d').pack()
        
        # Reading count
        count_frame = tk.Frame(info_frame, bg='white')
        count_frame.pack(side='right', padx=20)
        
        tk.Label(count_frame, text="Readings", 
                font=('Arial', 12), bg='white', fg='#34495e').pack()
        self.count_var = tk.StringVar(value="0")
        tk.Label(count_frame, textvariable=self.count_var,
                font=('Arial', 18, 'bold'), bg='white', fg='#9b59b6').pack()
        
        # Status indicators
        indicator_frame = tk.Frame(main_frame, bg='white')
        indicator_frame.pack(pady=10)
        
        self.zero_indicator = tk.Label(indicator_frame, text="●", 
                                     font=('Arial', 20), bg='white', fg='#95a5a6')
        self.zero_indicator.pack(side='left', padx=10)
        tk.Label(indicator_frame, text="Zero", 
                font=('Arial', 10), bg='white', fg='#7f8c8d').pack(side='left')
        
        self.weight_indicator = tk.Label(indicator_frame, text="●", 
                                       font=('Arial', 20), bg='white', fg='#95a5a6')
        self.weight_indicator.pack(side='right', padx=10)
        tk.Label(indicator_frame, text="Weight Detected", 
                font=('Arial', 10), bg='white', fg='#7f8c8d').pack(side='right')
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(button_frame, text="Start", 
                                    command=self.start_reading,
                                    font=('Arial', 12), 
                                    bg='#27ae60', fg='white',
                                    padx=20, pady=5)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(button_frame, text="Stop", 
                                   command=self.stop_reading,
                                   font=('Arial', 12), 
                                   bg='#e74c3c', fg='white',
                                   padx=20, pady=5, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.tare_button = tk.Button(button_frame, text="Tare (Zero)", 
                                   command=self.tare_scale,
                                   font=('Arial', 12), 
                                   bg='#3498db', fg='white',
                                   padx=20, pady=5)
        self.tare_button.pack(side='left', padx=5)
        
        # Initialize variables
        self.reading_count = 0
        
        # Auto-start after a short delay
        self.root.after(1000, self.start_reading)
        
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
            
            # Update UI
            self.status_label.config(text="Status: Connected", fg='#27ae60')
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
        except serial.SerialException as e:
            self.status_label.config(text=f"Status: Serial Error - {str(e)}", fg='#e74c3c')
        except Exception as e:
            self.status_label.config(text=f"Status: Error - {str(e)}", fg='#e74c3c')
    
    def stop_reading(self):
        self.is_running = False
        if self.serial_connection:
            self.serial_connection.close()
        
        # Update UI
        self.status_label.config(text="Status: Disconnected", fg='#e74c3c')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
    
    def tare_scale(self):
        # Simple tare - just record current reading as new zero
        if hasattr(self, 'last_raw_reading'):
            self.tare_point = self.last_raw_reading
            self.status_label.config(text="Status: Tared", fg='#f39c12')
            # Reset back to connected after 2 seconds
            self.root.after(2000, lambda: self.status_label.config(text="Status: Connected", fg='#27ae60'))
    
    def read_serial_data(self):
        # Skip initial messages
        time.sleep(1)
        for _ in range(5):
            if self.serial_connection:
                self.serial_connection.readline()
        
        while self.is_running and self.serial_connection:
            try:
                line = self.serial_connection.readline()
                if line:
                    decoded = line.decode('utf-8', errors='ignore').strip()
                    if ',' in decoded and decoded.split(',')[0].isdigit():
                        parts = decoded.split(',')
                        if len(parts) >= 4:
                            raw_lbs = float(parts[1])
                            temp = float(parts[3])
                            
                            # Convert to grams and subtract tare point
                            raw_grams = raw_lbs * 453.592
                            self.last_raw_reading = raw_grams
                            weight_grams = raw_grams - self.tare_point
                            
                            # Update GUI in main thread
                            self.root.after(0, self.update_display, weight_grams, temp)
                            
            except Exception as e:
                print(f"Error reading serial data: {e}")
                break
    
    def update_display(self, weight, temperature):
        # Update weight
        if abs(weight) < 5:  # Within 5g, show as zero
            self.weight_var.set("0.0")
            self.weight_label.config(fg='#27ae60')  # Green for zero
            self.zero_indicator.config(fg='#27ae60')  # Green indicator
            self.weight_indicator.config(fg='#95a5a6')  # Gray indicator
        else:
            self.weight_var.set(f"{weight:.1f}")
            if weight > 0:
                self.weight_label.config(fg='#e67e22')  # Orange for positive
            else:
                self.weight_label.config(fg='#3498db')  # Blue for negative
            self.zero_indicator.config(fg='#95a5a6')  # Gray indicator
            self.weight_indicator.config(fg='#e74c3c')  # Red for weight detected
        
        # Update temperature
        self.temp_var.set(f"{temperature:.1f}")
        
        # Update reading count
        self.reading_count += 1
        self.count_var.set(str(self.reading_count))
    
    def on_closing(self):
        self.stop_reading()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OpenScaleGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
