#!/usr/bin/env python3
"""
Test script to verify interactive keyboard controls work properly
"""

import sys
import os

def test_keyboard_controls():
    print("=" * 60)
    print("TESTING INTERACTIVE KEYBOARD CONTROLS")
    print("=" * 60)
    print("This will test if the keyboard controls work properly.")
    print("\nExpected behavior:")
    print("- 'C' should capture reference barcode")
    print("- 'S' should start/stop production mode")
    print("- 'R' should reset reference")
    print("- 'L' should view logs")
    print("- 'Q' should quit")
    print("\nPress any key to continue...")
    input()
    
    print("\nStarting the barcode verification system...")
    print("You should see a camera window open.")
    print("Try pressing the keys: C, S, R, L, Q")
    print("\nPress Enter to start the system...")
    input()
    
    # Import and run the main system
    try:
        from production_line_verifier_BARCODE import BarcodeProductionVerifier
        verifier = BarcodeProductionVerifier()
        verifier.run()
    except KeyboardInterrupt:
        print("\nSystem interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_keyboard_controls()
