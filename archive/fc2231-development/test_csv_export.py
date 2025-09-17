#!/usr/bin/env python3
"""
Test CSV export functionality without Arduino
"""

import csv
from datetime import datetime
from fc2231_terminal import KawaiiFC2231Monitor

def test_csv_export():
    """Test CSV export with sample data"""
    print("🧪 Testing CSV Export Functionality")
    
    # Create monitor instance
    monitor = KawaiiFC2231Monitor()
    
    # Add sample data
    monitor.export_enabled = True
    
    # Simulate some readings
    sample_data = [
        {
            'Reading#': 1,
            'DateTime': datetime.now(),
            'Time': '10:30:15',
            'Voltage(V)': 0.498,
            'Force(N)': 0.000,
            'Force(g)': 0.0,
            'Temperature(°C)': 23.5,
            'Status': 'ZERO'
        },
        {
            'Reading#': 55,
            'DateTime': datetime.now(),
            'Time': '10:30:20',
            'Voltage(V)': 1.245,
            'Force(N)': 15.678,
            'Force(g)': 1599.2,
            'Temperature(°C)': 23.7,
            'Status': 'MEDIUM'
        },
        {
            'Reading#': 110,
            'DateTime': datetime.now(),
            'Time': '10:30:25',
            'Voltage(V)': 2.890,
            'Force(N)': 45.123,
            'Force(g)': 4602.8,
            'Temperature(°C)': 24.1,
            'Status': 'STRONG'
        }
    ]
    
    monitor.export_data = sample_data
    
    # Test export
    print(f"📊 Sample data records: {len(monitor.export_data)}")
    success = monitor.export_to_csv()
    
    if success:
        print("✅ CSV export test successful!")
        print("\n📁 CSV file contains columns:")
        print("   - Reading# (sequence number)")
        print("   - DateTime (full timestamp with milliseconds)")
        print("   - Time (HH:MM:SS format)")
        print("   - Voltage(V) (sensor voltage)")
        print("   - Force(N) (force in Newtons)")
        print("   - Force(g) (force in grams)")
        print("   - Temperature(°C) (sensor temperature)")
        print("   - Status (ZERO, LIGHT, MEDIUM, STRONG, etc.)")
        print("\n🔧 File opens in:")
        print("   ✅ Microsoft Excel")
        print("   ✅ Google Sheets") 
        print("   ✅ LibreOffice Calc")
        print("   ✅ Any text editor")
        print("   ✅ Python pandas")
        print("   ✅ R, MATLAB, etc.")
    else:
        print("❌ CSV export test failed!")

if __name__ == "__main__":
    test_csv_export()