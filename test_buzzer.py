#!/usr/bin/env python3
"""
Simple buzzer test for GPIO 17
Tests the buzzer with simple ON/OFF control
"""

import RPi.GPIO as GPIO
import time

BUZZER_PIN = 17

def test_buzzer():
    """Test buzzer with simple ON/OFF control"""
    print("=" * 50)
    print("TESTING BUZZER (GPIO 17)")
    print("=" * 50)
    print("Wiring: Buzzer + → GPIO 17, Buzzer - → GND")
    print("Testing simple ON/OFF control...")
    print()
    
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        GPIO.output(BUZZER_PIN, GPIO.LOW)  # Start with buzzer OFF
        
        print("1. Short beep (0.3s)")
        GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn ON
        time.sleep(0.3)
        GPIO.output(BUZZER_PIN, GPIO.LOW)   # Turn OFF
        time.sleep(0.5)
        
        print("2. Double beep")
        for _ in range(2):
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(0.1)
        time.sleep(0.5)
        
        print("3. Long beep (0.8s)")
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.8)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.5)
        
        print("4. Error pattern (3 quick beeps)")
        for _ in range(3):
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(0.1)
        time.sleep(0.5)
        
        print("5. Reference captured pattern (3 beeps)")
        for _ in range(3):
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(0.1)
        
        print()
        print("✅ Buzzer test completed!")
        print("If you heard the beeps, the buzzer is working correctly.")
        
    except Exception as e:
        print(f"❌ Buzzer test failed: {e}")
        print("Check wiring: Buzzer + → GPIO 17, Buzzer - → GND")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed.")

if __name__ == "__main__":
    test_buzzer()
