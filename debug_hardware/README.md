# Button & Buzzer Debugging Project

This is a separate debugging project specifically for testing the GPIO buttons and buzzer hardware used in the production line barcode verification system.

## 🎯 Purpose

This debugging tool helps you:
- Test button functionality independently
- Test buzzer patterns and tones
- Verify GPIO wiring and connections
- Debug hardware issues before running the main system

## 🔌 Hardware Configuration

The debugger uses the same GPIO pins as the main system:

| Component | GPIO Pin | Function |
|-----------|----------|----------|
| **Buzzer** | GPIO 17 | Audio feedback |
| **Start Button** | GPIO 22 | Start/Stop control |
| **Capture Button** | GPIO 27 | Capture reference |

## 🚀 Quick Start

### 1. Run Interactive Mode
```bash
cd /home/rp/Desktop/production_line_barcode_verifier/debug_hardware
python3 button_buzzer_debug.py
```

### 2. Run Specific Tests
```bash
# Test all buzzer patterns
python3 button_buzzer_debug.py buzzer

# Test buttons continuously
python3 button_buzzer_debug.py buttons

# Show current button states
python3 button_buzzer_debug.py states

# Single buzzer beep
python3 button_buzzer_debug.py beep
```

## 📋 Interactive Menu

When you run the debugger without arguments, you'll see this menu:

```
🔧 BUTTON & BUZZER DEBUG MENU
============================================================
1. Test buzzer patterns
2. Test buttons continuously
3. Show button states
4. Single buzzer beep
5. Print statistics
6. Exit
============================================================
```

## 🎵 Buzzer Test Patterns

The debugger tests these buzzer patterns:

| Pattern | Description | Duration |
|---------|-------------|----------|
| **Single beep** | One short beep | 0.3s |
| **Double beep** | Two quick beeps | 0.2s each |
| **Triple beep** | Three quick beeps | 0.2s each |
| **Error pattern** | Three very quick beeps | 0.1s each |
| **Long beep** | One long beep | 0.8s |

## 🔘 Button Testing

### Continuous Testing
- Press buttons to see real-time feedback
- Each button press triggers a different buzzer pattern
- Press Ctrl+C to stop

### Button States
- Shows current state of both buttons
- HIGH = not pressed, LOW = pressed
- Useful for debugging wiring issues

## 📊 Statistics

The debugger tracks:
- Number of start button presses
- Number of capture button presses
- Number of buzzer tests performed

## 🛠️ Troubleshooting

### Buzzer Not Working
1. Check wiring: Buzzer + → GPIO 17, Buzzer - → GND
2. Verify buzzer polarity
3. Test with: `python3 button_buzzer_debug.py buzzer`

### Buttons Not Responding
1. Check wiring: Button Pin 1 → GPIO, Button Pin 2 → GND
2. Verify pull-up resistors are working
3. Test with: `python3 button_buzzer_debug.py states`

### GPIO Library Issues
- The debugger automatically detects available GPIO libraries
- Falls back to simulation mode if no GPIO library is available
- Shows which library is being used at startup

## 🔍 Expected Output

### Successful Startup
```
✅ Using RPi.GPIO library
🔧 Button & Buzzer Debugger Initialized!
============================================================
HARDWARE CONFIGURATION:
  Buzzer: GPIO 17
  Start Button: GPIO 22
  Capture Button: GPIO 27
============================================================
✅ GPIO pins configured successfully
  🔌 Buzzer: GPIO 17 (OUTPUT)
  🔘 Start Button: GPIO 22 (INPUT with PUD_UP)
  🔘 Capture Button: GPIO 27 (INPUT with PUD_UP)
```

### Button Press Example
```
🔘 START BUTTON PRESSED! (#1)
🔊 Buzzer test #1: single pattern
```

### Button States Example
```
🔘 Start Button (GPIO 22): NOT PRESSED (raw: 1)
🔘 Capture Button (GPIO 27): NOT PRESSED (raw: 1)
```

## 🎯 Usage Workflow

1. **Wire your hardware** according to the GPIO configuration
2. **Run the debugger**: `python3 button_buzzer_debug.py`
3. **Test buzzer patterns** (option 1) to verify audio
4. **Test buttons continuously** (option 2) to verify input
5. **Check button states** (option 3) to debug wiring
6. **View statistics** (option 5) to see test results
7. **Exit** (option 6) when testing is complete

## 🔧 Integration with Main System

Once your hardware is working with this debugger, you can run the main system:

```bash
cd /home/rp/Desktop/production_line_barcode_verifier
python3 production_line_verifier_HARDWARE.py
```

The main system uses the same GPIO configuration, so if the debugger works, the main system should work too!

## 📁 File Structure

```
debug_hardware/
├── button_buzzer_debug.py  # Main debugging script
└── README.md              # This documentation
```

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your wiring matches the GPIO configuration
3. Ensure you have the required GPIO libraries installed
4. Check the main system's HARDWARE_SETUP.md for detailed wiring diagrams
