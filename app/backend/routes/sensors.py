from flask import Blueprint, jsonify
import socket
import minimalmodbus

bp = Blueprint('sensors', __name__, url_prefix='/sensors')

# Global variables for RPM counting
pulse_count = 0

@bp.route('/rpm', methods=['GET'])
def get_rpm():
    global pulse_count
    try:
        # Simulate RPM reading for now (you can implement actual GPIO logic)
        rpm = pulse_count * 60  # Convert pulses to RPM
        return jsonify({"status": "success", "rpm": rpm})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/power', methods=['GET'])
def get_power():
    try:
        # Try to connect to power supply
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("192.168.1.141", 50505))
        
        # Send SCPI commands
        sock.send(b"MEAS:VOLT?\n")
        voltage = float(sock.recv(1024).decode().strip())
        
        sock.send(b"MEAS:CURR?\n")
        current = float(sock.recv(1024).decode().strip())
        
        sock.close()
        
        return jsonify({
            "status": "success", 
            "voltage": voltage, 
            "current": current
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Could not connect to power supply: {str(e)}"
        }), 500

@bp.route('/force', methods=['GET'])
def get_force():
    try:
        # Try to connect to force sensor
        instr = minimalmodbus.Instrument('/dev/ttyUSB0', 1, mode=minimalmodbus.MODE_RTU)
        instr.serial.baudrate = 9600
        instr.serial.bytesize = 8
        instr.serial.parity = minimalmodbus.serial.PARITY_NONE
        instr.serial.stopbits = 1
        instr.serial.timeout = 0.5
        instr.clear_buffers_before_each_transaction = True
        
        force = instr.read_register(0x0000, number_of_decimals=2, functioncode=3, signed=True)
        
        return jsonify({"status": "success", "force": force})
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Could not connect to force sensor: {str(e)}"
        }), 500
