from litestar import Litestar, get, post
from litestar.response import Response
import json
import os
import time
import csv
import socket
import minimalmodbus
import bluerobotics_navigator as navigator
from bluerobotics_navigator import PwmChannel, AdcChannel
from gpiozero import Device, DigitalInputDevice
from gpiozero.pins.rpigpio import RPiGPIOFactory

# Initialize GPIO factory for Raspberry Pi
#Device.pin_factory = RPiGPIOFactory()

# Initialize Navigator
navigator.init()
navigator.set_pwm_freq_hz(333)

# Global variables
pulse_count = 0
#rpm_pin = DigitalInputDevice(18)

def count_pulse():
    global pulse_count
    pulse_count += 1

rpm_pin.when_activated = count_pulse

# Thruster control functions
def set_thruster_pwm(pwm_channel=1, duty_cycle=0.5):
    navigator.set_pwm_enable(True)
    navigator.set_pwm_channel_duty_cycle(PwmChannel.Ch1, duty_cycle)

def read_rpm(pulses_per_rev=7, sample_time=0.25):
    global pulse_count
    pulse_count = 0
    time.sleep(sample_time)
    freq = pulse_count / sample_time
    rpm = freq * 60 / pulses_per_rev
    return rpm

# Power supply functions
def init_sl25(ip="192.168.1.141", port=50505):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        return sock
    except:
        return None

def scpi_query(sock, cmd):
    if sock:
        try:
            sock.send((cmd + "\n").encode())
            return sock.recv(1024).decode().strip()
        except:
            return "0"
    return "0"

def read_voltage_current(sock):
    try:
        voltage = float(scpi_query(sock, "MEAS:VOLT?"))
        current = float(scpi_query(sock, "MEAS:CURR?"))
        return voltage, current
    except:
        return 0.0, 0.0

# Force sensor functions
def init_rs485_force_sensor():
    try:
        instr = minimalmodbus.Instrument('/dev/ttyUSB0', 1, mode=minimalmodbus.MODE_RTU)
        instr.serial.baudrate = 9600
        instr.serial.bytesize = 8
        instr.serial.parity = minimalmodbus.serial.PARITY_NONE
        instr.serial.stopbits = 1
        instr.serial.timeout = 0.5
        instr.clear_buffers_before_each_transaction = True
        return instr
    except:
        return None

def read_rs485_force(instr):
    if instr:
        try:
            return instr.read_register(0x0000, number_of_decimals=2, functioncode=3, signed=True)
        except:
            return None
    return None

# API endpoints
@get("/")
async def root() -> dict:
    return {"message": "BR Thruster Destroyer Extension", "status": "running"}

@get("/status")
async def get_status() -> dict:
    return {
        "navigator_initialized": True,
        "pwm_enabled": navigator.get_pwm_enable(),
        "pwm_frequency": navigator.get_pwm_freq_hz()
    }

@post("/thruster/start")
async def start_thruster(data: dict) -> dict:
    duty_cycle = data.get("duty_cycle", 0.5)
    channel = data.get("channel", 1)
    
    try:
        set_thruster_pwm(channel, duty_cycle)
        return {"status": "success", "duty_cycle": duty_cycle, "channel": channel}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@post("/thruster/stop")
async def stop_thruster() -> dict:
    try:
        set_thruster_pwm(1, 0.5)  # Return to neutral
        navigator.set_pwm_enable(False)
        return {"status": "success", "message": "Thruster stopped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@get("/sensors/rpm")
async def get_rpm() -> dict:
    try:
        rpm = read_rpm()
        return {"status": "success", "rpm": rpm}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@get("/sensors/power")
async def get_power() -> dict:
    try:
        sock = init_sl25()
        if sock:
            voltage, current = read_voltage_current(sock)
            sock.close()
            return {"status": "success", "voltage": voltage, "current": current}
        else:
            return {"status": "error", "message": "Could not connect to power supply"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@get("/sensors/force")
async def get_force() -> dict:
    try:
        instr = init_rs485_force_sensor()
        if instr:
            force = read_rs485_force(instr)
            return {"status": "success", "force": force}
        else:
            return {"status": "error", "message": "Could not connect to force sensor"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@post("/test/start")
async def start_test(data: dict) -> dict:
    duration = data.get("duration", 10)
    duty_cycle = data.get("duty_cycle", 0.6327)
    
    try:
        # Start thruster
        set_thruster_pwm(1, duty_cycle)
        
        # Create log file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"thruster_test_{timestamp}.csv"
        
        # Initialize sensors
        power_sock = init_sl25()
        force_instr = init_rs485_force_sensor()
        
        # Start logging
        start_time = time.time()
        data_points = []
        
        while time.time() - start_time < duration:
            timestamp = time.time()
            
            # Read sensors
            rpm = read_rpm()
            voltage, current = read_voltage_current(power_sock) if power_sock else (0, 0)
            force = read_rs485_force(force_instr) if force_instr else None
            
            data_point = {
                "timestamp": timestamp,
                "rpm": rpm,
                "voltage": voltage,
                "current": current,
                "force": force,
                "duty_cycle": duty_cycle
            }
            data_points.append(data_point)
            
            time.sleep(0.25)  # 4Hz sampling
        
        # Stop thruster
        set_thruster_pwm(1, 0.5)
        
        # Save data
        if data_points:
            os.makedirs("logs", exist_ok=True)
            with open(f"logs/{filename}", 'w', newline='') as csvfile:
                fieldnames = data_points[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_points)
        
        # Cleanup
        if power_sock:
            power_sock.close()
        
        return {
            "status": "success",
            "duration": duration,
            "data_points": len(data_points),
            "filename": filename
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Create the Litestar app
app = Litestar(
    title="BR Thruster Destroyer",
    description="BlueOS Extension for Thruster Testing and Data Logging",
    version="0.0.1",
    route_handlers=[
        root,
        get_status,
        start_thruster,
        stop_thruster,
        get_rpm,
        get_power,
        get_force,
        start_test
    ]
)
