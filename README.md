# ESP32 MicroPython Thermostat

A smart thermostat built with MicroPython for ESP32, featuring temperature control, WiFi connectivity, MQTT integration, and an OLED display with rotary encoder interface.

## Features

- **Temperature Control**: Automated heating control via relay
- **Environmental Monitoring**: BME280 sensor for temperature, humidity, and pressure
- **User Interface**: SH1106 OLED display with rotary encoder control
- **Connectivity**: WiFi support with MQTT integration for home automation
- **Operating Modes**: Multiple thermostat modes (auto, heat, off)
- **Remote Control**: MQTT topics for remote temperature and mode control

## Hardware Requirements

### Components
- ESP32 variant (I used an ESP32-C6-Zero)
- BME280 temperature/humidity/pressure sensor
- SH1106 128x64 OLED display
- Rotary encoder with button
- Relay module (for heating control)

### Pin Configuration

| Component | Pin | ESP32 Pin |
|-----------|-----|-----------|
| Rotary Encoder CLK | Input | GPIO 2 |
| Rotary Encoder DT | Input | GPIO 3 |
| Rotary Encoder SW | Input | GPIO 4 |
| Relay Control | Output | GPIO 5 |
| I2C SCL | I2C Clock | GPIO 22 |
| I2C SDA | I2C Data | GPIO 21 |

## Software Requirements

### Development Environment
- Python 3.14+
- MicroPython 1.27+ firmware on ESP32
- mpremote tool for deployment

### Python Dependencies
These are only required for a better development experience
See `requirements.txt`:
```
micropython-esp32-stubs==1.27.0.post1
micropython-stdlib-stubs==1.27.0
mpremote==1.27.0
platformdirs==4.5.1
pyserial==3.5
```

## Installation

### 1. Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd thermostat

# Create virtual environment
python -m venv .venv
source ./.venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Device
Copy `template.config.py` to `src/config.py` and update with your settings:
The ID should be unique in your MQTT environment.

```python
# src/config.py
from micropython import const

ID = const("your_thermostat_id")
WLAN_SSID = const('your_wifi_ssid')
WLAN_PASSWORD = const('your_wifi_password')
MQTT_BROKER = const("your_homeassistant_host / or other mqtt_broker.")
MQTT_USER = const("your_mqtt_user")
MQTT_PASSWORD = const("your_mqtt_password")
```

### 3. Flash to ESP32
```bash
# Make flash script executable (if needed)
chmod +x flash.sh

# Flash the device
./flash.sh
```

## Project Structure

```
thermostat/
├── src/
│   ├── main.py              # Main application entry point
│   ├── config.py            # Device configuration (WLAN, MQTT credentials)
│   ├── boot.py              # Boot script
│   ├── thermostat.py         # BME280 sensor interface
│   ├── display.py           # OLED display management
│   ├── rotary_encoder.py    # Rotary encoder handling
│   ├── relay.py             # Relay control logic
│   ├── state.py             # Application state management
│   ├── mode.py              # Thermostat operating modes
│   ├── wlan.py              # WiFi connection handling
│   ├── mqtt.py              # MQTT client and topics
│   ├── asyncio_extensions.py # Async utilities
│   └── lib/
│       ├── bme280.py        # BME280 sensor driver
│       └── sh1106.py        # SH1106 display driver
├── template.config.py       # Configuration template
├── flash.sh                 # Deployment script
├── requirements.txt          # Python dependencies
└── README.md               # This file
```

## Usage

### Physical Interface
- **Rotary Encoder**: Adjust target temperature (±0.5°C steps)
- **Button**: Cycle through operating modes
- **Display**: Shows current temperature, humidity, target temperature, and mode

### MQTT Topics
- `your_id/temperature_set`: Set target temperature
- `your_id/mode_set`: Set operating mode
- `your_id/temperature`: Current temperature
- `your_id/humidity`: Current humidity
- `your_id/pressure`: Current pressure

### Operating Modes
The thermostat supports multiple modes controlled via the button or MQTT:
- **Off**: Heating/cooling disabled
- **Heat**: Enable heating permanently
- **Auto**: Automatic heating based on target

## Temperature Control

### Target Temperature Range
- **Minimum**: 7.0°C
- **Maximum**: 25.0°C
- **Step Size**: 0.5°C

### Control Logic
The thermostat compares current temperature with target temperature and controls the relay based on the selected mode.
There is a threshold for the relay of ±0.2 degrees to ensure the relay does not constantly switch around the setpoint.

## Development

### Testing
```bash
# Connect to device for debugging
mpremote
```

### Code Style
- Use type hints where possible
- Async/await for concurrent operations
- Event-driven architecture with subscriptions

### Dependencies
The project uses:
- **MicroPython**: Python implementation for microcontrollers
- **Asyncio**: Event loop for concurrent operations
- **MQTT**: Message queuing for telemetry transport
- **I2C**: Communication protocol for sensors and display

## Troubleshooting

### Common Issues

1. **WiFi Connection Fails**
   - Check SSID and password in `config.py`
   - Verify network availability
   - Check signal strength

2. **MQTT Connection Issues**
   - Verify broker address and credentials
   - Check network connectivity
   - Confirm broker is running

3. **Display Not Working**
   - Check I2C connections (SDA/SCL)
   - Verify power supply

4. **Sensor Reading Errors**
   - Verify BME280 connections
   - Check I2C address conflicts
   - Ensure sensor is powered

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the code documentation
- Open an issue in the repository