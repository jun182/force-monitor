#!/usr/bin/env python3
"""
Test script for Force Monitor export functionality
==================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import statistics
import csv

# Mock data for testing export
test_session_weights = [10.5, 15.2, 8.7, 22.1, 12.9, 18.6, 7.3, 25.4, 11.8, 19.2]
test_tare_offset = -33.9975
test_session_start_time = datetime.now()

def test_export_data():
    """Test the export data functionality"""
    print("🌸 Testing Force Monitor Export Function 🌸")
    
    if not test_session_weights:
        print("❌ No data to export!")
        return
        
    filename = f"test_force_monitor_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
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
            writer.writerow(['⚖️ Tare Offset (g)', f'{test_tare_offset:.4f}'])
            writer.writerow(['🔢 Total Readings', len(test_session_weights)])
            writer.writerow(['⏱️ Session Duration', "Test Session"])
            writer.writerow([])  # Empty row
            
            # Write statistics with emojis
            writer.writerow(['📊 Statistics'])
            if test_session_weights:
                writer.writerow(['📉 Minimum (g)', f'{min(test_session_weights):.2f}'])
                writer.writerow(['📈 Maximum (g)', f'{max(test_session_weights):.2f}'])
                writer.writerow(['📊 Average (g)', f'{statistics.mean(test_session_weights):.2f}'])
                writer.writerow(['📏 Std Deviation (g)', f'{statistics.stdev(test_session_weights) if len(test_session_weights) > 1 else 0:.2f}'])
            writer.writerow([])  # Empty row
            
            # Write data points
            writer.writerow(['📋 Reading #', 'Weight (g)', 'Timestamp'])
            for i, weight in enumerate(test_session_weights):
                timestamp = (test_session_start_time + 
                           timedelta(seconds=i*0.5)).strftime('%H:%M:%S')
                writer.writerow([i+1, f'{weight:.2f}', timestamp])
        
        print(f"✅ Export test successful! File created: {filename}")
        print(f"📊 Exported {len(test_session_weights)} data points")
        print(f"📈 Max: {max(test_session_weights):.2f}g")
        print(f"📉 Min: {min(test_session_weights):.2f}g") 
        print(f"📊 Average: {statistics.mean(test_session_weights):.2f}g")
        
    except Exception as e:
        print(f"❌ Export test failed: {str(e)}")

if __name__ == "__main__":
    test_export_data()
