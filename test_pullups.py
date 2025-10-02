#!/usr/bin/env python3
"""
Test script to verify internal pull-up resistors are working correctly
"""

import RPi.GPIO as GPIO
import time

# GPIO Pin Configuration
START_BTN_PIN = 22   # Start/Stop button on GPIO 22
CAPTURE_BTN_PIN = 27 # Capture reference button on GPIO 27

def test_pullups():
    """Test internal pull-up resistors"""
    print("=" * 60)
    print("TESTING INTERNAL PULL-UP RESISTORS")
    print("=" * 60)
    
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup button pins with internal pull-up resistors
        GPIO.setup(START_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(CAPTURE_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print("GPIO pins configured with internal pull-ups:")
        print(f"  Start Button (GPIO {START_BTN_PIN}): Pull-up enabled")
        print(f"  Capture Button (GPIO {CAPTURE_BTN_PIN}): Pull-up enabled")
        print()
        
        # Test button states
        print("Testing button states (should read HIGH when not pressed):")
        print(f"  Start Button (GPIO {START_BTN_PIN}): {GPIO.input(START_BTN_PIN)} (1=HIGH, 0=LOW)")
        print(f"  Capture Button (GPIO {CAPTURE_BTN_PIN}): {GPIO.input(CAPTURE_BTN_PIN)} (1=HIGH, 0=LOW)")
        print()
        
        if GPIO.input(START_BTN_PIN) == GPIO.HIGH and GPIO.input(CAPTURE_BTN_PIN) == GPIO.HIGH:
            print("✅ SUCCESS: Both buttons read HIGH (pull-ups working)")
            print("   - Buttons should read HIGH when not pressed")
            print("   - Buttons should read LOW when pressed")
        else:
            print("⚠️  WARNING: Buttons not reading HIGH")
            print("   - Check wiring connections")
            print("   - Verify buttons are normally open")
        
        print()
        print("Button wiring with internal pull-ups:")
        print(f"  Start Button: GPIO {START_BTN_PIN} → Button Pin 1")
        print(f"                GND → Button Pin 2")
        print(f"  Capture Button: GPIO {CAPTURE_BTN_PIN} → Button Pin 1")
        print(f"                  GND → Button Pin 2")
        print()
        print("Press buttons to test (Ctrl+C to exit):")
        
        last_start_state = GPIO.HIGH
        last_capture_state = GPIO.HIGH
        
        while True:
            # Check start button
            start_state = GPIO.input(START_BTN_PIN)
            if start_state == GPIO.LOW and last_start_state == GPIO.HIGH:
                print(f"🔴 Start Button (GPIO {START_BTN_PIN}) PRESSED!")
            elif start_state == GPIO.HIGH and last_start_state == GPIO.LOW:
                print(f"🟢 Start Button (GPIO {START_BTN_PIN}) RELEASED!")
            last_start_state = start_state
            
            # Check capture button
            capture_state = GPIO.input(CAPTURE_BTN_PIN)
            if capture_state == GPIO.LOW and last_capture_state == GPIO.HIGH:
                print(f"🔴 Capture Button (GPIO {CAPTURE_BTN_PIN}) PRESSED!")
            elif capture_state == GPIO.HIGH and last_capture_state == GPIO.LOW:
                print(f"🟢 Capture Button (GPIO {CAPTURE_BTN_PIN}) RELEASED!")
            last_capture_state = capture_state
            
            time.sleep(0.01)  # Small delay
            
    except KeyboardInterrupt:
        print("\nTest completed!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed.")

if __name__ == "__main__":
    test_pullups()
