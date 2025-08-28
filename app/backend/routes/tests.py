from flask import Blueprint, request, jsonify
import os
import time
import csv
from .thruster import start_thruster, stop_thruster
from .sensors import get_rpm, get_power, get_force

bp = Blueprint('tests', __name__, url_prefix='/tests')

@bp.route('/start', methods=['POST'])
def start_test():
    data = request.get_json()
    duration = data.get("duration", 10)
    duty_cycle = data.get("duty_cycle", 0.6327)
    
    try:
        # Start thruster
        start_result = start_thruster()
        if start_result.status_code != 200:
            return start_result
        
        # Create log file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"thruster_test_{timestamp}.csv"
        
        # Start logging
        start_time = time.time()
        data_points = []
        
        while time.time() - start_time < duration:
            timestamp = time.time()
            
            # Read sensors
            rpm_data = get_rpm().get_json()
            power_data = get_power().get_json()
            force_data = get_force().get_json()
            
            data_point = {
                "timestamp": timestamp,
                "rpm": rpm_data.get("rpm", 0) if rpm_data["status"] == "success" else 0,
                "voltage": power_data.get("voltage", 0) if power_data["status"] == "success" else 0,
                "current": power_data.get("current", 0) if power_data["status"] == "success" else 0,
                "force": force_data.get("force", 0) if force_data["status"] == "success" else 0,
                "duty_cycle": duty_cycle
            }
            data_points.append(data_point)
            
            time.sleep(0.25)  # 4Hz sampling
        
        # Stop thruster
        stop_thruster()
        
        # Save data
        if data_points:
            os.makedirs("logs", exist_ok=True)
            with open(f"logs/{filename}", 'w', newline='') as csvfile:
                fieldnames = data_points[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_points)
        
        return jsonify({
            "status": "success",
            "duration": duration,
            "data_points": len(data_points),
            "filename": filename
        })
        
    except Exception as e:
        # Ensure thruster is stopped on error
        try:
            stop_thruster()
        except:
            pass
        return jsonify({"status": "error", "message": str(e)}), 500
