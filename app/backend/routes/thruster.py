from flask import Blueprint, request, jsonify
import time

bp = Blueprint('thruster', __name__, url_prefix='/thruster')

# Try to import Navigator, fallback if not available
try:
    import bluerobotics_navigator as navigator
    from bluerobotics_navigator import PwmChannel
    NAVIGATOR_AVAILABLE = True
    navigator.init()
    navigator.set_pwm_freq_hz(333)
except ImportError:
    NAVIGATOR_AVAILABLE = False
    print("Warning: Navigator package not available, thruster control disabled")

@bp.route('/start', methods=['POST'])
def start_thruster():
    if not NAVIGATOR_AVAILABLE:
        return jsonify({"status": "error", "message": "Navigator not available"}), 400
    
    data = request.get_json()
    duty_cycle = data.get("duty_cycle", 0.5)
    channel = data.get("channel", 1)
    
    try:
        navigator.set_pwm_enable(True)
        navigator.set_pwm_channel_duty_cycle(PwmChannel.Ch1, duty_cycle)
        return jsonify({
            "status": "success", 
            "duty_cycle": duty_cycle, 
            "channel": channel
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/stop', methods=['POST'])
def stop_thruster():
    if not NAVIGATOR_AVAILABLE:
        return jsonify({"status": "error", "message": "Navigator not available"}), 400
    
    try:
        navigator.set_pwm_channel_duty_cycle(PwmChannel.Ch1, 0.5)  # Return to neutral
        navigator.set_pwm_enable(False)
        return jsonify({"status": "success", "message": "Thruster stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/status', methods=['GET'])
def thruster_status():
    if not NAVIGATOR_AVAILABLE:
        return jsonify({"status": "error", "message": "Navigator not available"}), 400
    
    try:
        return jsonify({
            "status": "success",
            "pwm_enabled": navigator.get_pwm_enable(),
            "pwm_frequency": navigator.get_pwm_freq_hz()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
