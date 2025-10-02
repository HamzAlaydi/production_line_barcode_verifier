# Hardware Test Application

A Python application for testing I2C LCD display and infrared proximity sensor on Raspberry Pi.

## Hardware Setup

### I2C LCD Display
- **Connection**: I2C LCD on GPIO SCL/SDA pins
- **I2C Bus**: 1 (default)
- **I2C Address**: 0x27 (default, can be changed)
- **Display**: 16x2 character LCD with I2C backpack

### Infrared Proximity Sensor
- **Connection**: GPIO pin 24
- **Pullup Resistor**: Internal pullup enabled (activated due to pulldown signal)
- **Type**: Photoelectric switch that detects when light beam is interrupted

### Buzzer
- **Connection**: GPIO pin 17
- **Type**: Active buzzer (3.3V or 5V compatible)
- **Function**: Audio feedback for obstacle detection

### Power Switch
- **Connection**: GPIO pin 22
- **Type**: Push button or toggle switch
- **Function**: Turn system monitoring on/off

## Wiring Diagram

```
Raspberry Pi          I2C LCD
-----------          --------
GPIO 2 (SDA)   -->   SDA
GPIO 3 (SCL)   -->   SCL
5V             -->   VCC
GND            -->   GND

Raspberry Pi          Proximity Sensor
-----------          ----------------
GPIO 24        -->   Signal
5V             -->   VCC
GND            -->   GND

Raspberry Pi          Buzzer
-----------          ------
GPIO 17        -->   Signal
5V             -->   VCC
GND            -->   GND

Raspberry Pi          Power Switch
-----------          -------------
GPIO 22        -->   Signal
GND            -->   GND
```

## Installation

### 1. Enable I2C on Raspberry Pi
```bash
sudo raspi-config
# Navigate to: Interfacing Options > I2C > Enable
sudo reboot
```

### 2. Install Dependencies
```bash
# Install system packages
sudo apt-get update
sudo apt-get install python3-rpi.gpio python3-smbus

# Or install via pip
pip install -r requirements.txt
```

### 3. Verify I2C Connection
```bash
# Check if I2C devices are detected
sudo i2cdetect -y 1

# Should show your LCD address (e.g., 0x27)
```

## Usage

### Basic Usage
```bash
# Run with real hardware
python3 main.py

# Run with simulator (for testing without hardware)
python3 main.py --simulator
```

### Command Line Options
```bash
python3 main.py [options]

Options:
  --simulator     Use simulator instead of real hardware
  --lcd-addr HEX  I2C address for LCD (default: 0x27)
  --sensor-pin N  GPIO pin for proximity sensor (default: 24)
  --buzzer-pin N  GPIO pin for buzzer (default: 17)
  --power-switch-pin N  GPIO pin for power switch (default: 22)
  --help          Show help message
```

### Examples
```bash
# Use different LCD address
python3 main.py --lcd-addr 0x3F

# Use different sensor pin
python3 main.py --sensor-pin 18

# Use different buzzer pin
python3 main.py --buzzer-pin 18

# Use different power switch pin
python3 main.py --power-switch-pin 18

# Test with simulator
python3 main.py --simulator
```

## Application Features

### LCD Display
- Shows current sensor status
- Displays obstacle detection count
- Real-time updates when sensor state changes
- Backlight control

### Proximity Sensor
- Monitors infrared beam interruption
- Internal pullup resistor for reliable detection
- Debounced input to prevent false triggers
- Callback-based event handling

### Buzzer
- Audio feedback for obstacle detection
- Different beep patterns based on detection count:
  - 1st detection: Single beep
  - 2-3 detections: Double beep
  - 4-10 detections: Triple beep
  - 10+ detections: Long beep

### Power Switch
- Toggle system monitoring on/off
- Press button to start monitoring
- Press again to stop monitoring
- Obstacle count resets when system turns on
- LCD shows system status (ON/OFF)

### Status Messages
- **"SYSTEM OFF"**: System is off, press switch to start
- **"SYSTEM ON"**: System is on and monitoring
- **"PATH CLEAR"**: No obstacle detected
- **"OBSTACLE DETECTED"**: Light beam interrupted
- **Count display**: Number of detections

## Code Structure

```
hardware_test/
├── main.py              # Main application
├── i2c_lcd.py          # I2C LCD driver
├── proximity_sensor.py # Proximity sensor handler
├── buzzer_control.py   # Buzzer control
├── power_switch.py     # Power switch control
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Key Classes

#### `I2CLCD`
- Handles I2C communication with LCD
- Supports 16x2 character displays
- Backlight control
- Text positioning and formatting

#### `ProximitySensor`
- GPIO pin management
- Pullup resistor configuration
- Interrupt-based event handling
- Debouncing for reliable detection

#### `BuzzerControl`
- GPIO pin management for buzzer
- Beep pattern generation
- Obstacle detection audio feedback
- Simulator support for testing

#### `PowerSwitch`
- GPIO pin management for power switch
- Toggle system on/off functionality
- Debounced input handling
- Simulator support for testing

#### `HardwareTestApp`
- Main application controller
- Coordinates LCD, sensor, buzzer, and power switch
- Handles user interface
- Graceful shutdown handling

## Troubleshooting

### I2C Issues
```bash
# Check I2C is enabled
lsmod | grep i2c

# Check for I2C devices
sudo i2cdetect -y 1

# Check I2C permissions
groups $USER
```

### GPIO Issues
```bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER
# Logout and login again

# Test GPIO access
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"
```

### Common Problems

1. **LCD not displaying**: Check I2C address and connections
2. **Sensor not responding**: Verify GPIO pin and pullup configuration
3. **Buzzer not working**: Check GPIO pin and power connections
4. **Power switch not working**: Verify GPIO pin and button connections
5. **Permission errors**: Add user to gpio group
6. **I2C not detected**: Enable I2C in raspi-config

## Testing

### Simulator Mode
Use simulator mode to test the application without hardware:
```bash
python3 main.py --simulator
```

### Manual Testing
1. Run the application
2. Press power switch to turn system ON
3. Verify LCD shows "SYSTEM ON"
4. Wave hand in front of proximity sensor
5. Verify LCD shows "OBSTACLE DETECTED"
6. Verify buzzer makes appropriate beep pattern
7. Remove obstacle and verify "PATH CLEAR" message
8. Test multiple detections to hear different beep patterns
9. Press power switch to turn system OFF
10. Verify LCD shows "SYSTEM OFF"

## Safety Notes

- Ensure proper voltage levels (5V for LCD, 3.3V for GPIO)
- Use appropriate pullup/pulldown resistors
- Avoid short circuits when wiring
- Disconnect power before making connections

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify hardware connections
3. Test with simulator mode first
4. Check system logs for errors
