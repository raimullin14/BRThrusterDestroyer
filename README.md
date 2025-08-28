# BR Thruster Destroyer

A BlueOS Extension for comprehensive thruster testing and data logging in underwater robotics applications.

## Overview

The BR Thruster Destroyer is a BlueOS extension that provides real-time control and monitoring of thruster systems while collecting comprehensive performance data. It's designed for research, development, and quality assurance testing of underwater thruster systems.

## Features

### 🚀 **Thruster Control**
- **PWM Control**: Direct control via Blue Robotics Navigator board
- **Configurable Duty Cycles**: 0-100% PWM control with real-time adjustment
- **Safety Features**: Automatic neutral position return and graceful shutdown

### 📊 **Data Collection**
- **Force Measurement**: RS485 force sensor integration for thrust measurement
- **Motor RPM**: GPIO-based pulse counting for motor speed monitoring
- **Power Metrics**: Voltage and current readings via SCPI protocol
- **Temperature Monitoring**: ADC channel monitoring for thermal data
- **Real-time Logging**: 4Hz data collection with timestamped CSV output

### 🔧 **Hardware Integration**
- **Blue Robotics Navigator**: PWM control and ADC reading
- **RS485 Communication**: Force sensor data acquisition
- **GPIO Interface**: RPM pulse counting and sensor interfacing
- **Network Communication**: SCPI protocol for power supply monitoring

### 🌐 **Web Interface**
- **Real-time Controls**: Live thruster control and parameter adjustment
- **Live Data Display**: Real-time sensor readings and system status
- **Test Management**: Automated test execution with configurable parameters
- **Data Visualization**: Test results and performance metrics display

## Installation

This extension is designed to be deployed as a BlueOS extension. It will be automatically built and deployed via GitHub Actions to Docker Hub and BlueOS.

### Prerequisites
- BlueOS system with Navigator board
- RS485 force sensor (optional)
- Power supply with SCPI interface (optional)
- GPIO access for RPM counting

### Manual Installation (Development)
```bash
# Clone the repository
git clone https://github.com/yourusername/BRThrusterDestroyer.git
cd BRThrusterDestroyer

# Install Python dependencies
cd app
pip install -e .
```

## Usage

### Web Interface
1. Access the extension through BlueOS
2. Use the control panel to adjust thruster parameters
3. Monitor real-time sensor data
4. Execute automated tests with custom parameters

### API Endpoints
- `GET /` - Extension status and information
- `GET /status` - System and Navigator status
- `POST /thruster/start` - Start thruster with specified duty cycle
- `POST /thruster/stop` - Stop thruster and return to neutral
- `GET /sensors/rpm` - Current RPM reading
- `GET /sensors/power` - Voltage and current readings
- `GET /sensors/force` - Force sensor reading
- `POST /test/start` - Execute automated test with logging

### Example API Usage
```bash
# Start thruster at 75% duty cycle
curl -X POST http://localhost:8000/thruster/start \
  -H "Content-Type: application/json" \
  -d '{"duty_cycle": 0.75}'

# Start a 30-second test at 60% duty cycle
curl -X POST http://localhost:8000/test/start \
  -H "Content-Type: application/json" \
  -d '{"duration": 30, "duty_cycle": 0.60}'
```

## Configuration

### Hardware Configuration
- **PWM Channel**: Default channel 1 (configurable)
- **PWM Frequency**: 333 Hz (optimized for thruster control)
- **GPIO Pin**: Pin 18 for RPM counting
- **Serial Port**: /dev/ttyUSB0 for RS485 communication
- **Network**: 192.168.1.141:50505 for power supply SCPI

### Test Parameters
- **Default Duration**: 10 seconds
- **Default Duty Cycle**: 63.27%
- **Sampling Rate**: 4 Hz (0.25 second intervals)
- **Data Format**: CSV with timestamp, RPM, voltage, current, force, duty cycle

## Data Output

Test data is automatically saved to timestamped CSV files in the `logs/` directory:
```
logs/
├── thruster_test_20250126_143022.csv
├── thruster_test_20250126_143156.csv
└── ...
```

Each CSV contains:
- Timestamp (Unix time)
- RPM (revolutions per minute)
- Voltage (volts)
- Current (amperes)
- Force (newtons)
- Duty Cycle (0.0-1.0)

## Development

### Project Structure
```
BRThrusterDestroyer/
├── app/
│   ├── main.py                 # BlueOS extension backend
│   ├── thrustertestloggerbase.py  # Core thruster testing logic
│   ├── pyproject.toml         # Python dependencies
│   └── static/
│       ├── index.html         # Web interface
│       └── register_service   # BlueOS extension metadata
├── Dockerfile                 # Container configuration
├── .github/workflows/         # GitHub Actions for deployment
└── README.md                  # This file
```

### Building Locally
```bash
# Build Docker image
docker build -t br-thruster-destroyer .

# Run locally
docker run -p 8000:8000 --privileged \
  -v /dev/ttyUSB0:/dev/ttyUSB0 \
  -v /dev/gpiomem:/dev/gpiomem \
  br-thruster-destroyer
```

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure the container runs with `--privileged` flag
2. **Device Not Found**: Check device paths and permissions
3. **Communication Errors**: Verify network settings and hardware connections
4. **GPIO Access**: Ensure `/dev/gpiomem` is accessible

### Debug Mode
Enable debug logging by setting environment variables:
```bash
export PYTHONPATH=/app
export DEBUG=1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check BlueOS documentation
- Review the API documentation at `/docs` endpoint

## Acknowledgments

- Blue Robotics for Navigator board support
- BlueOS community for extension framework
- Contributors and testers

---

**⚠️ Safety Notice**: This extension controls high-power thruster systems. Always ensure proper safety measures are in place before testing. Never operate thrusters without proper supervision and safety protocols.
