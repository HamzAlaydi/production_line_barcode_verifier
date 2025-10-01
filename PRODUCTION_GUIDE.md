# Production Line Barcode Verification System

## 🎯 Purpose
This system ensures every product on the production line has the correct barcode by comparing scanned barcodes against a reference barcode.

## 📋 Features
- ✅ Reference barcode capture
- ✅ Real-time production verification (40 items/min capability)
- ✅ Three detection states:
  - **PASS**: Barcode matches reference
  - **MISMATCH**: Wrong barcode detected
  - **NO BARCODE**: Empty or damaged product
- ✅ Audio alerts (different sounds for each status)
- ✅ CSV logging for traceability
- ✅ Real-time statistics
- ✅ Visual feedback on screen

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install opencv-python pyzbar numpy
```

### 2. Run the System
```bash
python production_line_verifier.py
```

### 3. Capture Reference Barcode
1. Place a **correct product** in front of the camera
2. Press **'C'** key to capture the reference barcode
3. Wait for confirmation: "✅ REFERENCE BARCODE CAPTURED!"

### 4. Start Production Verification
1. Press **'S'** key to start production mode
2. System will automatically scan products every 1.5 seconds
3. Watch for alerts:
   - **✓ PASS** - Green box, short beep
   - **❌ MISMATCH** - Red box, double beep
   - **⚠️ NO BARCODE** - Long low beep

### 5. Monitor Results
- Check real-time statistics on screen
- Press **'L'** to view recent logs
- All results saved to `production_log.csv`

## ⌨️ Keyboard Controls (Laptop Testing)

| Key | Function |
|-----|----------|
| **C** | Capture reference barcode |
| **S** | Start/Stop production verification |
| **R** | Reset reference barcode |
| **L** | View recent logs |
| **H** | Show help |
| **Q** | Quit system |

## 🔊 Audio Alerts

- **Reference Captured**: 3 ascending beeps
- **Pass/Success**: 1 short high beep (1000 Hz)
- **Mismatch**: 2 medium beeps (800 Hz)
- **No Barcode**: 1 long low beep (400 Hz)

## 📊 Performance Specifications

- **Throughput**: Up to 40 items per minute
- **Scan Interval**: 1.5 seconds per item
- **Camera Resolution**: 1280x720 @ 30 FPS
- **Detection Methods**: ZBar (pyzbar) with image enhancement

## 🔧 For Raspberry Pi Deployment

### Hardware Setup
1. Connect Raspberry Pi Camera or USB camera
2. Connect two push buttons:
   - GPIO Pin for Capture Button
   - GPIO Pin for Start/Stop Button
3. Connect buzzer for audio alerts
4. Optional: Connect LCD display

### Software Modifications Needed
Replace keyboard controls with GPIO:
```python
# Replace line 12 import
import RPi.GPIO as GPIO

# Add GPIO setup
CAPTURE_BUTTON_PIN = 17
START_BUTTON_PIN = 27
BUZZER_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(CAPTURE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(START_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Replace winsound with GPIO buzzer control
```

## 📝 Log File Format

The system creates `production_log.csv` with these columns:
- **Timestamp**: Date and time of scan
- **Status**: PASS, MISMATCH, NO_BARCODE, REFERENCE_SET
- **Barcode**: Detected barcode value
- **Reference**: Reference barcode value
- **Type**: Barcode type (CODE128, EAN13, etc.)

Example:
```csv
Timestamp,Status,Barcode,Reference,Type
2025-09-30 14:30:15.123,REFERENCE_SET,1234567890,1234567890,CODE128
2025-09-30 14:30:20.456,PASS,1234567890,1234567890,CODE128
2025-09-30 14:30:22.789,MISMATCH,9876543210,1234567890,CODE128
2025-09-30 14:30:25.012,NO_BARCODE,,,
```

## 🧪 Testing Workflow

### Test 1: Reference Capture
1. Start system
2. Show a barcode to camera
3. Press 'C'
4. Verify reference is captured and displayed

### Test 2: Matching Product
1. Show same barcode as reference
2. Press 'S' to start production
3. Verify: Green box, "PASS" message, short beep

### Test 3: Wrong Product (Mismatch)
1. Show different barcode
2. Verify: Red box, "MISMATCH" alert, double beep

### Test 4: No Barcode
1. Show blank/no product
2. Verify: "NO BARCODE" alert, long beep

### Test 5: Performance
1. Test with rapid barcode changes
2. Verify system processes at 1.5s intervals
3. Check logs are recorded correctly

## ⚠️ Important Notes

1. **Lighting**: Ensure good, consistent lighting for reliable detection
2. **Camera Focus**: Adjust camera focus for sharp barcode images
3. **Barcode Size**: Barcodes should be clearly visible (not too small)
4. **Distance**: Optimal distance: 15-30 cm from camera
5. **Stability**: Mount camera firmly to avoid vibration

## 🎯 Production Checklist

Before starting production:
- [ ] Camera is properly mounted and focused
- [ ] Reference barcode is captured correctly
- [ ] Audio alerts are working
- [ ] Lighting is adequate
- [ ] Test with sample products (pass/fail/no barcode)
- [ ] Verify log file is being created
- [ ] Train operators on system usage

## 📞 Troubleshooting

### Problem: No camera detected
- **Solution**: Check camera connection, ensure no other app is using camera

### Problem: Barcode not detected
- **Solution**: Improve lighting, adjust camera focus, ensure barcode is clean

### Problem: Wrong detection rate
- **Solution**: Adjust camera distance, improve image quality, clean camera lens

### Problem: Audio not working (Windows)
- **Solution**: Check system volume, ensure speakers/audio device is connected

### Problem: Slow performance
- **Solution**: Close other applications, use dedicated USB camera, reduce resolution

## 📈 Future Enhancements

- [ ] Multiple reference barcodes support
- [ ] Database integration
- [ ] Remote monitoring dashboard
- [ ] Email/SMS alerts
- [ ] Product counting
- [ ] Shift-based reporting
- [ ] Barcode print quality assessment

