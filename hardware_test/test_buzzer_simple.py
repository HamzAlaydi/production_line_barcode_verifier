#!/usr/bin/env python3
"""
Simple buzzer test script
"""

import time
from buzzer_control import BuzzerControl

def test_buzzer():
    print("Testing buzzer on GPIO 17...")
    
    try:
        buzzer = BuzzerControl(pin=17)
        
        print("Making single beep...")
        buzzer.beep(0.3)
        time.sleep(1)
        
        print("Making double beep...")
        buzzer.beep_pattern("double", 1)
        time.sleep(1)
        
        print("Making triple beep...")
        buzzer.beep_pattern("triple", 1)
        time.sleep(1)
        
        print("Making long beep...")
        buzzer.beep_pattern("long", 1)
        time.sleep(1)
        
        print("Buzzer test complete!")
        buzzer.cleanup()
        
    except Exception as e:
        print(f"Error testing buzzer: {e}")

if __name__ == "__main__":
    test_buzzer()
