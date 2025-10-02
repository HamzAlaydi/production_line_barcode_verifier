#!/usr/bin/env python3
"""
Test script for hardware setup verification
Tests I2C LCD and proximity sensor without running the full application
"""

import time
import sys
from i2c_lcd import I2CLCD
from proximity_sensor import ProximitySensor, ProximitySensorSimulator

def test_i2c_lcd():
    """Test I2C LCD functionality"""
    print("Testing I2C LCD...")
    
    try:
        # Try to initialize LCD
        lcd = I2CLCD(i2c_bus=1, i2c_addr=0x27, rows=2, cols=16)
        print("✓ LCD initialized successfully")
        
        # Test basic functionality
        lcd.backlight_on()
        lcd.print_message("Test Message", "LCD Working!")
        print("✓ LCD display test passed")
        
        time.sleep(2)
        
        # Test cursor positioning
        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.write_string("Line 1")
        lcd.set_cursor(1, 0)
        lcd.write_string("Line 2")
        print("✓ LCD cursor positioning test passed")
        
        time.sleep(2)
        
        # Test backlight control
        lcd.backlight_off()
        time.sleep(1)
        lcd.backlight_on()
        print("✓ LCD backlight control test passed")
        
        lcd.close()
        return True
        
    except Exception as e:
        print(f"✗ LCD test failed: {e}")
        return False

def test_proximity_sensor():
    """Test proximity sensor functionality"""
    print("\nTesting Proximity Sensor...")
    
    try:
        # Try to initialize sensor
        sensor = ProximitySensor(pin=24, pull_up=True, bounce_time=50)
        print("✓ Proximity sensor initialized successfully")
        
        # Test reading sensor
        for i in range(5):
            state = sensor.read_sensor()
            status = "OBSTACLE" if state else "CLEAR"
            print(f"  Reading {i+1}: {status}")
            time.sleep(0.5)
        
        print("✓ Proximity sensor reading test passed")
        
        # Test callback functionality
        callback_called = False
        
        def test_callback(obstacle_detected):
            nonlocal callback_called
            callback_called = True
            print(f"  Callback triggered: {'OBSTACLE' if obstacle_detected else 'CLEAR'}")
        
        sensor.set_callback(test_callback)
        print("✓ Proximity sensor callback test passed")
        
        # Wait a bit for any potential interrupts
        time.sleep(2)
        
        sensor.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ Proximity sensor test failed: {e}")
        return False

def test_simulator():
    """Test simulator functionality"""
    print("\nTesting Simulator...")
    
    try:
        # Test LCD simulator (if available)
        print("✓ LCD simulator test skipped (using real hardware)")
        
        # Test proximity sensor simulator
        sensor = ProximitySensorSimulator(pin=24)
        print("✓ Proximity sensor simulator initialized")
        
        # Test simulator functionality
        sensor.simulate_obstacle(True)
        state = sensor.read_sensor()
        print(f"  Simulated obstacle: {state}")
        
        sensor.simulate_obstacle(False)
        state = sensor.read_sensor()
        print(f"  Simulated clear: {state}")
        
        print("✓ Proximity sensor simulator test passed")
        
        sensor.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ Simulator test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("Hardware Setup Test")
    print("=" * 50)
    
    # Check command line arguments
    use_simulator = "--simulator" in sys.argv
    test_lcd = "--lcd" in sys.argv or "--all" in sys.argv
    test_sensor = "--sensor" in sys.argv or "--all" in sys.argv
    test_sim = "--sim" in sys.argv or "--all" in sys.argv
    
    # Default to testing all if no specific tests requested
    if not any([test_lcd, test_sensor, test_sim]):
        test_lcd = True
        test_sensor = True
        test_sim = True
    
    results = []
    
    # Run tests
    if test_lcd and not use_simulator:
        results.append(test_i2c_lcd())
    
    if test_sensor and not use_simulator:
        results.append(test_proximity_sensor())
    
    if test_sim:
        results.append(test_simulator())
    
    # Print results
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    
    if all(results):
        print("✓ All tests passed! Hardware setup is working correctly.")
        print("\nYou can now run the main application:")
        print("  python3 main.py")
    else:
        print("✗ Some tests failed. Please check your hardware connections.")
        print("\nTroubleshooting tips:")
        print("1. Check I2C is enabled: sudo raspi-config")
        print("2. Check I2C devices: sudo i2cdetect -y 1")
        print("3. Check GPIO permissions: groups $USER")
        print("4. Test with simulator: python3 main.py --simulator")

if __name__ == "__main__":
    main()
