#!/usr/bin/env python3
"""
FC2231 Calibration Manager - Persistent Calibration System
==========================================================

Author: Johnny Hamnesjö Olausson
Email: johnny.hamnesjo@chalmers.se
Institution: Chalmers University of Technology
Department: Department of Industrial and Materials Science

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import json
import os
import statistics
from datetime import datetime
from typing import Dict, Optional, List

class FC2231CalibrationManager:
    """Manages persistent calibration data for FC2231 force sensors"""
    
    def __init__(self, calibration_file: str = "fc2231_calibration.json"):
        self.calibration_file = calibration_file
        self.default_calibration = {
            "tare_voltage": 0.5,  # Default minimum voltage
            "max_force_newtons": 100.0,  # Maximum force in Newtons
            "voltage_min": 0.5,   # FC2231 minimum output voltage
            "voltage_max": 4.5,   # FC2231 maximum output voltage
            "calibration_date": None,
            "calibration_stability": None,
            "known_force_calibration": None,  # For multi-point calibration
            "serial_port": "COM3",  # Default Arduino COM port
            "arduino_board": "Uno R3",
            "sensor_model": "FC2231",
            "version": "1.0"
        }
        
    def load_calibration(self) -> Dict:
        """Load calibration data from file, create default if not exists"""
        try:
            if os.path.exists(self.calibration_file):
                with open(self.calibration_file, 'r') as f:
                    data = json.load(f)
                    
                # Validate and update structure if needed
                for key, default_value in self.default_calibration.items():
                    if key not in data:
                        data[key] = default_value
                
                print(f"✅ Loaded FC2231 calibration from {self.calibration_file}")
                print(f"   📅 Calibrated: {data['calibration_date'] or 'Never'}")
                print(f"   ⚡ Tare voltage: {data['tare_voltage']:.4f}V")
                print(f"   💪 Max force: {data['max_force_newtons']:.1f}N")
                return data
            else:
                print(f"⚠️  No FC2231 calibration file found, using defaults")
                return self.default_calibration.copy()
                
        except Exception as e:
            print(f"❌ Error loading FC2231 calibration: {e}")
            print("🔄 Using default calibration")
            return self.default_calibration.copy()
    
    def save_calibration(self, calibration_data: Dict) -> bool:
        """Save calibration data to file"""
        try:
            # Add timestamp
            calibration_data["calibration_date"] = datetime.now().isoformat()
            calibration_data["version"] = "1.0"
            
            with open(self.calibration_file, 'w') as f:
                json.dump(calibration_data, f, indent=4)
            
            print(f"✅ FC2231 calibration saved to {self.calibration_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving FC2231 calibration: {e}")
            return False
    
    def perform_voltage_tare(self, voltage_readings: List[float]) -> Dict:
        """Perform tare calibration using voltage readings"""
        if len(voltage_readings) < 5:
            raise ValueError("Need at least 5 voltage readings for calibration")
        
        # Calculate statistics
        tare_voltage = statistics.mean(voltage_readings)
        stability = statistics.stdev(voltage_readings)
        
        # Load existing calibration and update tare
        calibration_data = self.load_calibration()
        calibration_data.update({
            "tare_voltage": tare_voltage,
            "calibration_date": datetime.now().isoformat(),
            "calibration_stability": stability,
            "version": "1.0"
        })
        
        return calibration_data
    
    def perform_force_calibration(self, empty_voltages: List[float], 
                                 loaded_voltages: List[float], 
                                 known_force_newtons: float) -> Dict:
        """Perform full force calibration with known weight"""
        if len(empty_voltages) < 5 or len(loaded_voltages) < 5:
            raise ValueError("Need at least 5 readings for each state")
        
        # Calculate baselines
        empty_voltage = statistics.mean(empty_voltages)
        loaded_voltage = statistics.mean(loaded_voltages)
        
        # Calculate voltage change per Newton
        voltage_change = loaded_voltage - empty_voltage
        voltage_per_newton = voltage_change / known_force_newtons if known_force_newtons != 0 else 0
        
        # Calculate maximum force based on voltage range
        voltage_range = 4.5 - empty_voltage  # From tare to max voltage
        max_force = voltage_range / voltage_per_newton if voltage_per_newton != 0 else 100.0
        
        # Calculate stability
        empty_stability = statistics.stdev(empty_voltages)
        loaded_stability = statistics.stdev(loaded_voltages)
        overall_stability = max(empty_stability, loaded_stability)
        
        # Create calibration data
        calibration_data = {
            "tare_voltage": empty_voltage,
            "max_force_newtons": max_force,
            "voltage_min": 0.5,
            "voltage_max": 4.5,
            "calibration_date": datetime.now().isoformat(),
            "calibration_stability": overall_stability,
            "known_force_calibration": {
                "force_newtons": known_force_newtons,
                "voltage_change": voltage_change,
                "voltage_per_newton": voltage_per_newton
            },
            "serial_port": "COM4",
            "arduino_board": "Uno R3",
            "sensor_model": "FC2231",
            "version": "1.0"
        }
        
        return calibration_data
    
    def voltage_to_force(self, voltage: float, calibration_data: Dict) -> float:
        """Convert voltage reading to force in Newtons"""
        tare_voltage = calibration_data.get("tare_voltage", 0.5)
        max_force = calibration_data.get("max_force_newtons", 100.0)
        voltage_min = calibration_data.get("voltage_min", 0.5)
        voltage_max = calibration_data.get("voltage_max", 4.5)
        
        # Apply tare
        adjusted_voltage = voltage - tare_voltage + voltage_min
        
        # Clamp to valid range
        if adjusted_voltage < voltage_min:
            adjusted_voltage = voltage_min
        if adjusted_voltage > voltage_max:
            adjusted_voltage = voltage_max
        
        # Linear conversion
        voltage_range = voltage_max - voltage_min
        voltage_ratio = (adjusted_voltage - voltage_min) / voltage_range
        force_newtons = voltage_ratio * max_force
        
        return force_newtons
    
    def force_to_grams(self, force_newtons: float) -> float:
        """Convert force from Newtons to grams-force"""
        return force_newtons * 101.97  # 1 N = 101.97 grams-force
    
    def get_calibration_status(self, calibration_data: Dict) -> str:
        """Get human-readable calibration status"""
        if not calibration_data.get("calibration_date"):
            return "❌ Never calibrated"
        
        try:
            cal_date = datetime.fromisoformat(calibration_data["calibration_date"])
            days_ago = (datetime.now() - cal_date).days
            
            stability = calibration_data.get("calibration_stability", float('inf'))
            
            # Determine status based on age and stability
            if days_ago == 0:
                age_status = "today"
            elif days_ago == 1:
                age_status = "yesterday"
            elif days_ago < 7:
                age_status = f"{days_ago} days ago"
            elif days_ago < 30:
                age_status = f"{days_ago//7} weeks ago"
            else:
                age_status = f"{days_ago//30} months ago"
            
            # Stability assessment for voltage (different thresholds than weight)
            if stability < 0.001:  # 1mV
                stability_status = "🟢 Excellent"
            elif stability < 0.005:  # 5mV
                stability_status = "🟡 Good"
            elif stability < 0.02:   # 20mV
                stability_status = "🟠 Fair"
            else:
                stability_status = "🔴 Poor"
            
            return f"✅ Calibrated {age_status} | {stability_status} stability"
            
        except Exception:
            return "⚠️  Calibration data corrupted"
    
    def validate_calibration(self, calibration_data: Dict) -> bool:
        """Validate calibration data integrity"""
        required_keys = ["tare_voltage", "max_force_newtons", "voltage_min", "voltage_max"]
        
        for key in required_keys:
            if key not in calibration_data:
                return False
        
        # Check for reasonable values
        tare_voltage = calibration_data["tare_voltage"]
        max_force = calibration_data["max_force_newtons"]
        
        if not isinstance(tare_voltage, (int, float)) or not isinstance(max_force, (int, float)):
            return False
        
        # Validate voltage range
        if tare_voltage < 0.4 or tare_voltage > 5.0:
            return False
        
        # Validate force range
        if max_force <= 0 or max_force > 10000:  # Reasonable force limits
            return False
        
        return True

if __name__ == "__main__":
    # Test the FC2231 calibration manager
    print("🌸 Testing FC2231 Calibration Manager 🌸")
    
    cal_manager = FC2231CalibrationManager()
    
    # Load existing or create default
    cal_data = cal_manager.load_calibration()
    print(f"\nStatus: {cal_manager.get_calibration_status(cal_data)}")
    
    # Test voltage to force conversion
    test_voltages = [0.5, 1.0, 2.0, 3.0, 4.5]
    print(f"\n📊 Voltage to Force Conversion Test:")
    for voltage in test_voltages:
        force_n = cal_manager.voltage_to_force(voltage, cal_data)
        force_g = cal_manager.force_to_grams(force_n)
        print(f"  {voltage:.1f}V → {force_n:.2f}N ({force_g:.1f}g)")