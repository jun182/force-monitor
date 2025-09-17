#!/usr/bin/env python3
"""
Calibration Manager - Persistent Calibration System
===================================================

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

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os
import statistics
from datetime import datetime
from typing import Dict, Optional, List

class CalibrationManager:
    """Manages persistent calibration data for the force monitor system"""
    
    def __init__(self, calibration_file: str = "force_monitor_calibration.json"):
        self.calibration_file = calibration_file
        self.default_calibration = {
            "tare_offset": 0.0,
            "scale_factor": 1.0,
            "calibration_date": None,
            "calibration_stability": None,
            "calibration_weight": None,
            "serial_port": "COM4",
            "version": "2.0"
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
                
                print(f"✅ Loaded calibration from {self.calibration_file}")
                print(f"   📅 Calibrated: {data['calibration_date'] or 'Never'}")
                print(f"   ⚖️  Tare offset: {data['tare_offset']:.4f}g")
                return data
            else:
                print(f"⚠️  No calibration file found, using defaults")
                return self.default_calibration.copy()
                
        except Exception as e:
            print(f"❌ Error loading calibration: {e}")
            print("🔄 Using default calibration")
            return self.default_calibration.copy()
    
    def save_calibration(self, calibration_data: Dict) -> bool:
        """Save calibration data to file"""
        try:
            # Add timestamp
            calibration_data["calibration_date"] = datetime.now().isoformat()
            calibration_data["version"] = "2.0"
            
            with open(self.calibration_file, 'w') as f:
                json.dump(calibration_data, f, indent=4)
            
            print(f"✅ Calibration saved to {self.calibration_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving calibration: {e}")
            return False
    
    def perform_tare_calibration(self, raw_readings: List[float]) -> Dict:
        """Process raw readings to create tare calibration"""
        if len(raw_readings) < 5:
            raise ValueError("Need at least 5 readings for calibration")
        
        # Calculate statistics
        tare_offset = statistics.mean(raw_readings)
        stability = statistics.stdev(raw_readings)
        
        # Create calibration data
        calibration_data = {
            "tare_offset": tare_offset,
            "scale_factor": 1.0,  # Keep existing or default
            "calibration_date": datetime.now().isoformat(),
            "calibration_stability": stability,
            "calibration_weight": 0.0,  # This was a tare (zero) calibration
            "serial_port": "COM4",
            "version": "2.0"
        }
        
        return calibration_data
    
    def perform_weight_calibration(self, empty_readings: List[float], 
                                 loaded_readings: List[float], 
                                 known_weight: float) -> Dict:
        """Perform full weight calibration with known weight"""
        if len(empty_readings) < 5 or len(loaded_readings) < 5:
            raise ValueError("Need at least 5 readings for each state")
        
        # Calculate baselines
        empty_baseline = statistics.mean(empty_readings)
        loaded_baseline = statistics.mean(loaded_readings)
        
        # Calculate scale factor
        raw_change = loaded_baseline - empty_baseline
        scale_factor = raw_change / known_weight if known_weight != 0 else 1.0
        
        # Calculate stability
        empty_stability = statistics.stdev(empty_readings)
        loaded_stability = statistics.stdev(loaded_readings)
        overall_stability = max(empty_stability, loaded_stability)
        
        # Create calibration data
        calibration_data = {
            "tare_offset": empty_baseline,
            "scale_factor": scale_factor,
            "calibration_date": datetime.now().isoformat(),
            "calibration_stability": overall_stability,
            "calibration_weight": known_weight,
            "serial_port": "COM4",
            "version": "2.0"
        }
        
        return calibration_data
    
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
            
            # Stability assessment
            if stability < 10:
                stability_status = "🟢 Excellent"
            elif stability < 50:
                stability_status = "🟡 Good"
            elif stability < 200:
                stability_status = "🟠 Fair"
            else:
                stability_status = "🔴 Poor"
            
            return f"✅ Calibrated {age_status} | {stability_status} stability"
            
        except Exception:
            return "⚠️  Calibration data corrupted"
    
    def apply_calibration(self, raw_value: float, calibration_data: Dict) -> float:
        """Apply calibration to raw reading"""
        tare_offset = calibration_data.get("tare_offset", 0.0)
        scale_factor = calibration_data.get("scale_factor", 1.0)
        
        # Apply tare and scale factor
        tared_value = raw_value - tare_offset
        calibrated_value = tared_value / scale_factor if scale_factor != 0 else tared_value
        
        return calibrated_value
    
    def backup_calibration(self) -> bool:
        """Create a backup of current calibration"""
        try:
            if os.path.exists(self.calibration_file):
                backup_name = f"{self.calibration_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                import shutil
                shutil.copy2(self.calibration_file, backup_name)
                print(f"📦 Calibration backed up to {backup_name}")
                return True
            return False
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def validate_calibration(self, calibration_data: Dict) -> bool:
        """Validate calibration data integrity"""
        required_keys = ["tare_offset", "scale_factor", "version"]
        
        for key in required_keys:
            if key not in calibration_data:
                return False
        
        # Check for reasonable values
        tare_offset = calibration_data["tare_offset"]
        scale_factor = calibration_data["scale_factor"]
        
        if not isinstance(tare_offset, (int, float)) or not isinstance(scale_factor, (int, float)):
            return False
        
        if scale_factor == 0 or abs(scale_factor) > 1000:
            return False
        
        return True

if __name__ == "__main__":
    # Test the calibration manager
    print("🌸 Testing Calibration Manager 🌸")
    
    cal_manager = CalibrationManager()
    
    # Load existing or create default
    cal_data = cal_manager.load_calibration()
    print(f"\nStatus: {cal_manager.get_calibration_status(cal_data)}")
    
    # Test applying calibration
    test_raw = 100.0
    calibrated = cal_manager.apply_calibration(test_raw, cal_data)
    print(f"\nTest: {test_raw}g raw → {calibrated:.2f}g calibrated")
