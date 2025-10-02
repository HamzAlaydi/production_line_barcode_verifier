#!/usr/bin/env python3
"""
Test script for hardware integration
Tests GPIO buttons, buzzer, and LCD display
"""

import time
import sys

# GPIO imports with fallback
try:
    from gpiozero import Button, Buzzer
    GPIOZERO_AVAILABLE = True
    print("✓ GPIOZero library available")
except ImportError:
    GPIOZERO_AVAILABLE = False
    print("⚠ GPIOZero not available")

# LCD imports with fallback
try:
    from RPLCD.i2c import CharLCD
    LCD_AVAILABLE = True
    print("✓ RPLCD library available")
except ImportError:
    LCD_AVAILABLE = False
    print("⚠ RPLCD not available")

def test_hardware():
    """Test all hardware components"""
    print("\n" + "=" * 60)
    print("HARDWARE INTEGRATION TEST")
    print("=" * 60)
    
    # Test GPIO
    if GPIOZERO_AVAILABLE:
        try:
            print("\nTesting GPIO components...")
            
            # Test buzzer
            print("Testing buzzer (GPIO 17)...")
            buzzer = Buzzer(17)
            buzzer.on()
            time.sleep(0.5)
            buzzer.off()
            print("✓ Buzzer test completed")
            
            # Test buttons
            print("Testing buttons...")
            capture_btn = Button(22, pull_up=True)
            start_btn = Button(27, pull_up=True)
            
            print("✓ Buttons initialized")
            print("  - GPIO 22 (Capture): Ready")
            print("  - GPIO 27 (Start/Stop): Ready")
            
            # Test button states
            print(f"  - Capture button state: {'PRESSED' if not capture_btn.is_pressed else 'RELEASED'}")
            print(f"  - Start button state: {'PRESSED' if not start_btn.is_pressed else 'RELEASED'}")
            
            # Cleanup
            buzzer.close()
            capture_btn.close()
            start_btn.close()
            
        except Exception as e:
            print(f"⚠ GPIO test failed: {e}")
    else:
        print("⚠ GPIO test skipped - GPIOZero not available")
    
    # Test LCD
    if LCD_AVAILABLE:
        try:
            print("\nTesting LCD display...")
            lcd = CharLCD(i2c_expander='PCF8574', address=0x27, 
                         port=1, cols=16, rows=2, 
                         charmap='A02', auto_linebreaks=True)
            
            lcd.clear()
            lcd.write_string("Hardware Test")
            lcd.cursor_pos = (1, 0)
            lcd.write_string("All Systems OK")
            
            print("✓ LCD test completed")
            print("  - I2C address: 0x27")
            print("  - Display: 16x2 characters")
            
            time.sleep(2)
            lcd.close()
            
        except Exception as e:
            print(f"⚠ LCD test failed: {e}")
    else:
        print("⚠ LCD test skipped - RPLCD not available")
    
    print("\n" + "=" * 60)
    print("HARDWARE TEST SUMMARY")
    print("=" * 60)
    print(f"GPIO Zero: {'✓ Available' if GPIOZERO_AVAILABLE else '✗ Not Available'}")
    print(f"RPLCD: {'✓ Available' if LCD_AVAILABLE else '✗ Not Available'}")
    
    if GPIOZERO_AVAILABLE and LCD_AVAILABLE:
        print("\n🎉 All hardware components are ready!")
        print("You can now run the production line verifier with full hardware support.")
    else:
        print("\n⚠ Some hardware components are not available.")
        print("The system will run with software fallbacks.")
    
    print("=" * 60)

if __name__ == "__main__":
    test_hardware()
