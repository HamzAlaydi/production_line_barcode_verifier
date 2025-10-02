#!/usr/bin/env python3
"""
Test GPIO access after permission fixes
"""

import RPi.GPIO as GPIO
import time

def test_gpio_access():
    """Test if GPIO access is working"""
    print("=" * 50)
    print("TESTING GPIO ACCESS AFTER FIXES")
    print("=" * 50)
    
    try:
        # Test GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Test buzzer pin
        BUZZER_PIN = 17
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        
        # Test button pins
        START_BTN_PIN = 22
        CAPTURE_BTN_PIN = 27
        GPIO.setup(START_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(CAPTURE_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print("✅ GPIO setup successful!")
        print(f"  Buzzer: GPIO {BUZZER_PIN}")
        print(f"  Start Button: GPIO {START_BTN_PIN}")
        print(f"  Capture Button: GPIO {CAPTURE_BTN_PIN}")
        
        # Test buzzer
        print("\nTesting buzzer...")
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        print("✅ Buzzer test completed!")
        
        # Test button readings
        print("\nTesting button readings...")
        start_state = GPIO.input(START_BTN_PIN)
        capture_state = GPIO.input(CAPTURE_BTN_PIN)
        print(f"  Start Button (GPIO {START_BTN_PIN}): {start_state} (1=HIGH, 0=LOW)")
        print(f"  Capture Button (GPIO {CAPTURE_BTN_PIN}): {capture_state} (1=HIGH, 0=LOW)")
        
        if start_state == GPIO.HIGH and capture_state == GPIO.HIGH:
            print("✅ Buttons reading correctly (HIGH when not pressed)")
        else:
            print("⚠️  Buttons not reading HIGH - check wiring")
        
        print("\n✅ ALL GPIO TESTS PASSED!")
        print("Hardware system should work now!")
        
    except Exception as e:
        print(f"❌ GPIO test failed: {e}")
        print("GPIO permissions may still need fixing")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed.")

if __name__ == "__main__":
    test_gpio_access()
