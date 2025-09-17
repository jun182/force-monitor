#!/usr/bin/env python3
"""
Calibration Test Script
======================

Test script to demonstrate the persistent calibration system.
This creates and loads calibration data without needing the scale hardware.

Author: Johnny Hamnesjö Olausson
Email: johnny.hamnesjo@chalmers.se
"""

import random
from calibration_manager import CalibrationManager

def test_calibration_system():
    """Test the complete calibration workflow"""
    print("🌸 Testing Calibration System 🌸\n")
    
    # Initialize calibration manager
    cal_manager = CalibrationManager("test_calibration.json")
    
    # Test 1: Load default calibration
    print("📋 Test 1: Loading default calibration")
    cal_data = cal_manager.load_calibration()
    print(f"Status: {cal_manager.get_calibration_status(cal_data)}")
    print(f"Tare offset: {cal_data['tare_offset']:.4f}g\n")
    
    # Test 2: Simulate tare calibration
    print("📋 Test 2: Simulating tare calibration")
    # Generate fake readings around -50g with some noise
    fake_readings = [-50.0 + random.uniform(-2, 2) for _ in range(20)]
    print(f"Simulated readings: {len(fake_readings)} values around -50g")
    
    # Perform tare calibration
    tare_cal_data = cal_manager.perform_tare_calibration(fake_readings)
    print(f"New tare offset: {tare_cal_data['tare_offset']:.4f}g")
    print(f"Stability: ±{tare_cal_data['calibration_stability']:.2f}g")
    
    # Save calibration
    if cal_manager.save_calibration(tare_cal_data):
        print("✅ Calibration saved successfully\n")
    else:
        print("❌ Failed to save calibration\n")
    
    # Test 3: Load saved calibration
    print("📋 Test 3: Loading saved calibration")
    loaded_cal_data = cal_manager.load_calibration()
    print(f"Status: {cal_manager.get_calibration_status(loaded_cal_data)}")
    print(f"Loaded tare offset: {loaded_cal_data['tare_offset']:.4f}g\n")
    
    # Test 4: Apply calibration to readings
    print("📋 Test 4: Applying calibration to test readings")
    test_values = [loaded_cal_data['tare_offset'], 
                   loaded_cal_data['tare_offset'] + 100,
                   loaded_cal_data['tare_offset'] + 500,
                   loaded_cal_data['tare_offset'] - 50]
    
    for raw_value in test_values:
        calibrated = cal_manager.apply_calibration(raw_value, loaded_cal_data)
        print(f"Raw: {raw_value:>8.2f}g → Calibrated: {calibrated:>8.2f}g")
    
    print("\n✅ All tests completed!")
    print(f"📁 Test calibration saved to: test_calibration.json")

if __name__ == "__main__":
    test_calibration_system()
