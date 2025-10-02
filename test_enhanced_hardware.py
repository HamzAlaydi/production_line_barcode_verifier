#!/usr/bin/env python3
"""
Test Enhanced Production Line Hardware Integration
"""

from gpiozero import Button, Buzzer
from RPLCD.i2c import CharLCD
import time

# GPIO pins (matching production system)
BUZZER_PIN = 17
START_BTN_PIN = 22
CAPTURE_BTN_PIN = 27
LCD_ADDRESS = 0x27

def test_enhanced_hardware():
    """Test all hardware components for production line"""
    print("=== Enhanced Production Line Hardware Test ===")
    
    try:
        # Initialize hardware
        print("Initializing hardware...")
        buzzer = Buzzer(BUZZER_PIN)
        start_button = Button(START_BTN_PIN, pull_up=True)
        capture_button = Button(CAPTURE_BTN_PIN, pull_up=True)
        
        lcd = CharLCD('PCF8574', LCD_ADDRESS, cols=16, rows=2)
        lcd.clear()
        
        print("✓ All hardware initialized successfully!")
        
        # Test 1: LCD Display
        print("\nTest 1: LCD Display")
        lcd.write_string("Production Test")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Hardware OK")
        time.sleep(2)
        
        # Test 2: Buzzer
        print("\nTest 2: Buzzer")
        lcd.clear()
        lcd.write_string("Testing Buzzer")
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        print("✓ Buzzer test completed")
        time.sleep(1)
        
        # Test 3: Button States
        print("\nTest 3: Button States")
        lcd.clear()
        lcd.write_string("Button Test")
        lcd.cursor_pos = (1, 0)
        
        start_state = "PRESSED" if start_button.is_pressed else "RELEASED"
        capture_state = "PRESSED" if capture_button.is_pressed else "RELEASED"
        
        lcd.write_string(f"S:{start_state[:3]} C:{capture_state[:3]}")
        print(f"Start button: {start_state}")
        print(f"Capture button: {capture_state}")
        time.sleep(2)
        
        # Test 4: Button Event Simulation
        print("\nTest 4: Button Event Simulation")
        lcd.clear()
        lcd.write_string("Event Test")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Press buttons...")
        
        def on_start_press():
            lcd.clear()
            lcd.write_string("START PRESSED")
            buzzer.on()
            time.sleep(0.2)
            buzzer.off()
            print("Start button pressed!")
        
        def on_capture_press():
            lcd.clear()
            lcd.write_string("CAPTURE PRESSED")
            for _ in range(3):
                buzzer.on()
                time.sleep(0.1)
                buzzer.off()
                time.sleep(0.1)
            print("Capture button pressed!")
        
        # Set up event handlers
        start_button.when_pressed = on_start_press
        capture_button.when_pressed = on_capture_press
        
        print("Press buttons to test events (10 seconds)...")
        time.sleep(10)
        
        # Test 5: Production Simulation
        print("\nTest 5: Production Simulation")
        lcd.clear()
        lcd.write_string("Production Mode")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Simulating...")
        
        # Simulate production workflow
        for i in range(3):
            lcd.clear()
            lcd.write_string(f"Scan {i+1}/3")
            lcd.cursor_pos = (1, 0)
            lcd.write_string("Processing...")
            
            # Simulate scan result
            buzzer.on()
            time.sleep(0.3)
            buzzer.off()
            time.sleep(0.5)
        
        # Final status
        lcd.clear()
        lcd.write_string("Test Complete")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("All Systems OK")
        
        print("✓ Enhanced hardware test completed successfully!")
        print("All components ready for production line integration:")
        print("  - Buzzer (GPIO 17)")
        print("  - Start Button (GPIO 22)")
        print("  - Capture Button (GPIO 27)")
        print("  - LCD Display (I2C)")
        
        time.sleep(3)
        
    except Exception as e:
        print(f"✗ Hardware test failed: {e}")
    finally:
        try:
            buzzer.off()
            buzzer.close()
            start_button.close()
            capture_button.close()
            lcd.clear()
            lcd.close()
        except:
            pass

if __name__ == "__main__":
    test_enhanced_hardware()
