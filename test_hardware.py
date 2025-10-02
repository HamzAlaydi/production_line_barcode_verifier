#!/usr/bin/env python3
"""
Hardware Test Script for Barcode Verification System
Tests GPIO buzzer, buttons, and LCD display
"""

import RPi.GPIO as GPIO
import time
import sys

# GPIO Pin Configuration
BUZZER_PIN = 17      # Buzzer on GPIO 17
START_BTN_PIN = 22   # Start/Stop button on GPIO 22
CAPTURE_BTN_PIN = 27 # Capture reference button on GPIO 27

def setup_gpio():
    """Setup GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup buzzer pin
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    
    # Setup button pins with pull-up resistors
    GPIO.setup(START_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(CAPTURE_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    print("GPIO pins configured:")
    print(f"  Buzzer: GPIO {BUZZER_PIN}")
    print(f"  Start Button: GPIO {START_BTN_PIN}")
    print(f"  Capture Button: GPIO {CAPTURE_BTN_PIN}")

def test_buzzer():
    """Test buzzer with different tones"""
    print("\n" + "=" * 50)
    print("TESTING BUZZER (GPIO 17)")
    print("=" * 50)
    
    def buzzer_beep(frequency, duration):
        """Generate buzzer beep using PWM"""
        try:
            pwm = GPIO.PWM(BUZZER_PIN, frequency)
            pwm.start(50)  # 50% duty cycle
            time.sleep(duration)
            pwm.stop()
        except Exception as e:
            print(f"Buzzer error: {e}")
    
    print("Testing different buzzer tones...")
    
    # Test 1: Reference captured (3 ascending beeps)
    print("1. Reference captured tone (3 ascending beeps)")
    for freq in [1000, 1500, 2000]:
        buzzer_beep(freq, 0.2)
        time.sleep(0.1)
    
    time.sleep(1)
    
    # Test 2: Pass tone (short high beep)
    print("2. Pass tone (short high beep)")
    buzzer_beep(2000, 0.3)
    
    time.sleep(1)
    
    # Test 3: Mismatch tone (double medium beep)
    print("3. Mismatch tone (double medium beep)")
    buzzer_beep(1000, 0.2)
    time.sleep(0.1)
    buzzer_beep(1000, 0.2)
    
    time.sleep(1)
    
    # Test 4: No barcode tone (long low beep)
    print("4. No barcode tone (long low beep)")
    buzzer_beep(500, 0.8)
    
    time.sleep(1)
    
    # Test 5: Error tone (3 quick beeps)
    print("5. Error tone (3 quick beeps)")
    for _ in range(3):
        buzzer_beep(800, 0.1)
        time.sleep(0.1)
    
    print("Buzzer test completed!")

def test_buttons():
    """Test button functionality"""
    print("\n" + "=" * 50)
    print("TESTING BUTTONS")
    print("=" * 50)
    print("Press the buttons to test:")
    print(f"  GPIO {START_BTN_PIN} - Start/Stop button")
    print(f"  GPIO {CAPTURE_BTN_PIN} - Capture button")
    print("Press Ctrl+C to exit button test")
    
    last_start_state = GPIO.HIGH
    last_capture_state = GPIO.HIGH
    
    try:
        while True:
            # Check start button
            start_state = GPIO.input(START_BTN_PIN)
            if start_state == GPIO.LOW and last_start_state == GPIO.HIGH:
                print(f"[BUTTON] Start/Stop button (GPIO {START_BTN_PIN}) pressed!")
                # Quick beep for button press
                pwm = GPIO.PWM(BUZZER_PIN, 1500)
                pwm.start(50)
                time.sleep(0.1)
                pwm.stop()
            last_start_state = start_state
            
            # Check capture button
            capture_state = GPIO.input(CAPTURE_BTN_PIN)
            if capture_state == GPIO.LOW and last_capture_state == GPIO.HIGH:
                print(f"[BUTTON] Capture button (GPIO {CAPTURE_BTN_PIN}) pressed!")
                # Quick beep for button press
                pwm = GPIO.PWM(BUZZER_PIN, 2000)
                pwm.start(50)
                time.sleep(0.1)
                pwm.stop()
            last_capture_state = capture_state
            
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
            
    except KeyboardInterrupt:
        print("\nButton test completed!")

def test_lcd():
    """Test LCD display"""
    print("\n" + "=" * 50)
    print("TESTING LCD DISPLAY (I2C)")
    print("=" * 50)
    
    try:
        from RPLCD.i2c import CharLCD
        
        # Try common I2C addresses
        lcd_addresses = [0x27, 0x3F, 0x38]
        lcd = None
        
        for addr in lcd_addresses:
            try:
                print(f"Trying LCD at I2C address 0x{addr:02X}...")
                lcd = CharLCD('PCF8574', addr, cols=16, rows=2)
                lcd.clear()
                lcd.cursor_pos = (0, 0)
                lcd.write_string("LCD Test OK!")
                lcd.cursor_pos = (1, 0)
                lcd.write_string(f"Addr: 0x{addr:02X}")
                print(f"LCD found at address 0x{addr:02X}")
                break
            except Exception as e:
                print(f"  Failed: {e}")
                if lcd:
                    lcd.close()
                lcd = None
        
        if lcd:
            print("LCD test messages:")
            print("Line 1: LCD Test OK!")
            print("Line 2: Addr: 0xXX")
            
            # Test scrolling text
            time.sleep(2)
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string("Barcode Verifier")
            lcd.cursor_pos = (1, 0)
            lcd.write_string("Hardware Ready")
            
            time.sleep(2)
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string("System Status:")
            lcd.cursor_pos = (1, 0)
            lcd.write_string("All Tests Pass")
            
            time.sleep(2)
            lcd.close()
            print("LCD test completed!")
        else:
            print("LCD not found! Check connections:")
            print("  - SDA to GPIO 2 (Pin 3)")
            print("  - SCL to GPIO 3 (Pin 5)")
            print("  - VCC to 5V")
            print("  - GND to Ground")
            print("  - Common I2C addresses: 0x27, 0x3F, 0x38")
    
    except ImportError:
        print("RPLCD library not installed!")
        print("Install with: pip3 install RPLCD --break-system-packages")
    except Exception as e:
        print(f"LCD test error: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("HARDWARE TEST FOR BARCODE VERIFICATION SYSTEM")
    print("=" * 60)
    print("This script will test:")
    print("1. GPIO Buzzer (GPIO 17)")
    print("2. Buttons (GPIO 22, GPIO 27)")
    print("3. LCD Display (I2C)")
    print("=" * 60)
    
    try:
        # Setup GPIO
        setup_gpio()
        
        # Test buzzer
        test_buzzer()
        
        # Test LCD
        test_lcd()
        
        # Test buttons
        test_buttons()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        # Cleanup
        GPIO.cleanup()
        print("\nHardware test completed!")
        print("GPIO cleanup done.")

if __name__ == "__main__":
    main()
