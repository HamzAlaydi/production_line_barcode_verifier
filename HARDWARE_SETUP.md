# Hardware Setup Guide for Barcode Verification System

## 🔌 Wiring Diagram

### Raspberry Pi GPIO Connections

```
Raspberry Pi 5 GPIO Layout:
┌─────────────────────────────────────┐
│ 3.3V  │ 5V   │ GPIO2 │ 5V   │ GPIO3 │
│ GND   │ GPIO2│ GPIO3 │ GND  │ GPIO4 │
│ GPIO17│ GPIO27│ GPIO22│ 3.3V │ GPIO10│
│ GPIO11│ GPIO5 │ GPIO6 │ GPIO13│ GPIO19│
│ GND   │ GPIO26│ GPIO18│ GND  │ GPIO23│
│ GPIO24│ GND  │ GPIO25│ GPIO8 │ GPIO7 │
│ GND   │ GPIO12│ GND  │ GPIO16│ GPIO20│
│ GPIO21│ GND  │ GPIO4 │ GPIO17│ GPIO27│
└─────────────────────────────────────┘
```

### Component Connections

#### 1. Buzzer (GPIO 17) - ACTIVE BUZZER
```
Buzzer + (Positive) → GPIO 17 (Pin 11)
Buzzer - (Negative) → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
```
**Note**: Uses simple ON/OFF control (HIGH = ON, LOW = OFF)

#### 2. Start/Stop Button (GPIO 22) - WITH INTERNAL PULL-UP
```
Button Pin 1 → GPIO 22 (Pin 15)
Button Pin 2 → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
```
**Note**: Internal pull-up resistor enabled in software - no external resistor needed!

#### 3. Capture Button (GPIO 27) - WITH INTERNAL PULL-UP
```
Button Pin 1 → GPIO 27 (Pin 13)
Button Pin 2 → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
```
**Note**: Internal pull-up resistor enabled in software - no external resistor needed!

#### 4. LCD Display (I2C - Pins 2,3)
```
LCD VCC  → 5V (Pin 2 or 4)
LCD GND  → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
LCD SDA  → GPIO 2 (Pin 3) - SDA
LCD SCL  → GPIO 3 (Pin 5) - SCL
```

## 🎵 Buzzer Tones

| Action | Tone Pattern | Description |
|--------|--------------|-------------|
| **Reference Captured** | 3 short beeps | 0.2s each, 0.1s pause |
| **Pass/Success** | Short beep | 0.3s duration |
| **Mismatch** | Double beep | 0.2s each, 0.1s pause |
| **No Barcode** | Long beep | 0.8s duration |
| **Error** | 3 quick beeps | 0.1s each, 0.1s pause |
| **Start** | Start beep | 0.5s duration |
| **Stop** | Stop beep | 0.3s duration |

## 🎮 Button Functions

| Button | GPIO | Function | Action |
|--------|------|----------|--------|
| **Capture** | GPIO 27 | Capture Reference | Press to set reference barcode |
| **Start/Stop** | GPIO 22 | Toggle Production | Press to start/stop verification |

## 📺 LCD Display

### I2C Address
- Common addresses: `0x27`, `0x3F`, `0x38`
- The system will auto-detect the correct address

### Display Layout (16x2)
```
Line 1: Status/Title (16 chars)
Line 2: Details/Info (16 chars)
```

### Status Messages
- `"System Ready"` - Initial state
- `"Capturing..."` - When capturing reference
- `"Reference Set!"` - After successful capture
- `"Production ON"` - When verification is running
- `"Production OFF"` - When verification is paused
- `"PASS"` - When barcode matches
- `"MISMATCH!"` - When barcode doesn't match
- `"NO BARCODE"` - When no barcode detected

## 🔧 Setup Instructions

### 1. Enable I2C
```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
sudo reboot
```

### 2. Check I2C Devices
```bash
sudo i2cdetect -y 1
# Should show your LCD address (e.g., 0x27)
```

### 3. Test Hardware
```bash
cd /home/rp/Desktop/production_line_barcode_verifier
python3 test_hardware.py
```

### 4. Run Main System
```bash
python3 production_line_verifier_HARDWARE.py
```

## 🛠️ Troubleshooting

### Buzzer Not Working
- Check wiring to GPIO 17
- Verify buzzer polarity
- Test with: `python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.OUT); GPIO.output(17, GPIO.HIGH); import time; time.sleep(1); GPIO.output(17, GPIO.LOW); GPIO.cleanup()"`

### Buttons Not Responding
- Check wiring to GPIO 22 and GPIO 27
- Verify pull-up resistors are working
- Test with: `python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP); print('Button state:', GPIO.input(22))"`

### LCD Not Displaying
- Check I2C connections (SDA/SCL)
- Verify power connections (5V/GND)
- Check I2C address: `sudo i2cdetect -y 1`
- Try different I2C addresses in code

### Camera Issues
- Ensure DroidCam is running on phone
- Check network connection
- Verify IP address in camera sources list

## 📋 Parts List

| Component | Quantity | Notes |
|-----------|----------|-------|
| Raspberry Pi 5 | 1 | Main controller |
| Active Buzzer | 1 | 5V compatible |
| Push Buttons | 2 | Momentary, normally open |
| 16x2 LCD Display | 1 | I2C interface (PCF8574) |
| Jumper Wires | 6+ | Male-to-female for connections |
| Breadboard | 1 | Optional, for prototyping |
| ~~Resistors~~ | ~~0~~ | ~~Not needed - using internal pull-ups!~~ |

## 🎯 Usage Workflow

1. **Power on** Raspberry Pi
2. **Start DroidCam** on phone
3. **Run system**: `python3 production_line_verifier_HARDWARE.py`
4. **Point camera** at reference barcode
5. **Press Capture button** (GPIO 27) or 'C' key
6. **Press Start button** (GPIO 22) or 'S' key
7. **Show products** to camera for verification
8. **Listen for audio feedback** and check LCD status
9. **Press Start button** again to pause
10. **Press 'Q'** to quit and view statistics

## 🔍 Testing Commands

```bash
# Test all hardware components
python3 test_hardware.py

# Test buzzer only
sudo python3 test_buzzer.py

# Or test manually:
sudo python3 -c "
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
print('Testing buzzer...')
GPIO.output(17, GPIO.HIGH)  # Turn ON
time.sleep(0.5)
GPIO.output(17, GPIO.LOW)   # Turn OFF
print('Buzzer test completed')
GPIO.cleanup()
"

# Test buttons with internal pull-ups
python3 test_pullups.py

# Or test manually:
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print('Start button (GPIO 22):', GPIO.input(22), '(1=HIGH, 0=LOW)')
print('Capture button (GPIO 27):', GPIO.input(27), '(1=HIGH, 0=LOW)')
print('Both should read 1 (HIGH) when not pressed')
GPIO.cleanup()
"

# Test LCD
python3 -c "
from RPLCD.i2c import CharLCD
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)
lcd.write_string('Test OK!')
lcd.close()
"
```
