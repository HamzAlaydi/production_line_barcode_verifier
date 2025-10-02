#!/usr/bin/env python3
"""
Simple LCD test script
"""

import time
from i2c_lcd import I2CLCD

def test_lcd():
    print("Testing LCD on I2C address 0x27...")
    
    try:
        lcd = I2CLCD(i2c_bus=1, i2c_addr=0x27, rows=2, cols=16)
        lcd.backlight_on()
        
        print("Displaying test messages...")
        
        lcd.print_message("LCD Test", "Working!")
        time.sleep(2)
        
        lcd.print_message("System Ready", "Press button")
        time.sleep(2)
        
        lcd.print_message("Count: 0", "Status: OFF")
        time.sleep(2)
        
        lcd.print_message("Count: 5", "Status: ON")
        time.sleep(2)
        
        lcd.print_message("Goodbye!", "Test complete")
        time.sleep(2)
        
        lcd.backlight_off()
        lcd.close()
        
        print("LCD test complete!")
        
    except Exception as e:
        print(f"Error testing LCD: {e}")

if __name__ == "__main__":
    test_lcd()
