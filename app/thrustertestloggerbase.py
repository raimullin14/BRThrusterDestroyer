# Jupyter Notebook Structure for Thruster Control + Logging
# Blue Robotics Navigator (v0.0.6 Compatible)
# 2025-08-26 - Rai Mullin ft. ChatGPT

import os
# os.environ["DISABLE_LEAK"] = "true"  # Disable leak pin setup to avoid EBUSY crash - needed in v0.1.1
import time
import csv
import socket
import minimalmodbus
import bluerobotics_navigator as navigator
from bluerobotics_navigator import PwmChannel, AdcChannel

# from gpiozero import Device, DigitalInputDevice
# from gpiozero.pins.rpigpio import RPiGPIOFactory

# Device.pin_factory = RPiGPIOFactory()

# ---------- Navigator Initialization ----------
navigator.init()
navigator.set_pwm_freq_hz(333)  # Set PWM frequency

# ---------- PWM Thruster Output ----------
def set_thruster_pwm(pwm_channel=3, duty_cycle=0.5):
    # navigator v0.0.6 uses channel numbers directly (0–15)
    navigator.set_pwm_enable(True)
    navigator.set_pwm_channel_duty_cycle(PwmChannel.Ch1, 0.5)
    time.sleep(0.1)
    navigator.set_pwm_channel_duty_cycle(PwmChannel.Ch1, duty_cycle)

# ---------- RPM Counter via GPIO18 (Pin 12) ----------
# pulse_count = 0
# rpm_pin = DigitalInputDevice(18)

def count_pulse():
    global pulse_count
    pulse_count += 1

# rpm_pin.when_activated = count_pulse

def read_rpm(pulses_per_rev=7, sample_time=0.25):
    global pulse_count
    pulse_count = 0
    time.sleep(sample_time)
    freq = pulse_count / sample_time
    rpm = freq * 60 / pulses_per_rev
    return rpm

# ---------- SL25 Voltage/Current Reading via SCPI ----------
def init_sl25(ip="192.168.1.141", port=50505):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock

def scpi_query(sock, cmd):
    sock.send((cmd + "\n").encode())
    return sock.recv(1024).decode().strip()

def read_voltage_current(sock):
    try:
        voltage = float(scpi_query(sock, "MEAS:VOLT?"))
        current = float(scpi_query(sock, "MEAS:CURR?"))
        return voltage, current
    except:
        return 0.0, 0.0

# ---------- RS485 Force Sensor Logging ----------
def init_rs485_force_sensor():
    instr = minimalmodbus.Instrument('/dev/ttyUSB0', 1, mode=minimalmodbus.MODE_RTU)
    instr.serial.baudrate = 9600
    instr.serial.bytesize = 8
    instr.serial.parity   = minimalmodbus.serial.PARITY_NONE
    instr.serial.stopbits = 1
    instr.serial.timeout  = 0.5
    instr.clear_buffers_before_each_transaction = True
    return instr

def read_rs485_force(instr):
    try:
        return instr.read_register(0x0000, number_of_decimals=2, functioncode=3, signed=True)
    except:
        return None

def read_weight(instr):
    # get Sd (decimal places)
    sd = instr.read_register(0x0006, 0, functioncode=3, signed=False)
    sd = sd if 0 <= sd <= 5 else 0
    # get live weight at reg 1
    w  = instr.read_register(0x0001, sd, functioncode=3, signed=True)
    return w
        
# ---------- ADC Read for Force Sensor ----------
# def read_adc_force(channel=0):
#    return navigator.read_adc(AdcChannel.Ch0)

# ---------- Logging Function ----------
def start_logging(filename="thruster_log.csv", duration=30, pwm_channel=3, duty=0.5):
    os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None

    print("Starting logging...")
    sock = init_sl25()
    modbus = init_rs485_force_sensor()
    set_thruster_pwm(pwm_channel, duty)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "RS485_Force", "Motor_Temp_ADC1", "RPM", "Voltage", "Current", "PWM_Duty"])

        start_time = time.time()
        while time.time() - start_time < duration:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            force = read_weight(modbus)
            temp_adc1 = navigator.read_adc(AdcChannel.Ch1)
            rpm = read_rpm()
            voltage, current = read_voltage_current(sock)
            writer.writerow([timestamp, force, temp_adc1, rpm, voltage, current, duty])
            time.sleep(0.25)

    
    navigator.set_pwm_channel_duty_cycle(PwmChannel.Ch1, 0.5)
    navigator.set_pwm_enable(False)
    sock.close()
    print(f"Logging complete. Data saved to {filename}")

# ---------- Example Use ----------
# Uncomment to test run
start_logging(duration=10, duty=0.6327)

# upper_value = 0.6327 # Duty Cycle %
# lower_value = 0.3663 # Duty Cycle %