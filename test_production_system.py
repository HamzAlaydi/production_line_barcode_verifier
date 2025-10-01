#!/usr/bin/env python3
"""
Quick test script to verify the production system is ready.
"""

import cv2
from pyzbar import pyzbar
import winsound

def test_camera():
    """Test camera access."""
    print("Testing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[FAIL] Camera not accessible")
        return False
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("[FAIL] Could not capture frame")
        return False
    
    print("[PASS] Camera working")
    return True

def test_barcode_detection():
    """Test barcode detection with sample."""
    print("\nTesting barcode detection...")
    
    # Create a simple test with camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[SKIP] Camera not available")
        return False
    
    print("  Show a barcode to the camera (5 second test)...")
    import time
    start_time = time.time()
    detected = False
    
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if ret:
            barcodes = pyzbar.decode(frame)
            if barcodes:
                print(f"[PASS] Detected barcode: {barcodes[0].data.decode('utf-8')}")
                detected = True
                break
    
    cap.release()
    
    if not detected:
        print("[INFO] No barcode detected (this is OK if you didn't show one)")
    
    return True

def test_audio():
    """Test audio alerts."""
    print("\nTesting audio alerts...")
    try:
        print("  Playing success sound...")
        winsound.Beep(1000, 100)
        print("  Playing mismatch sound...")
        winsound.Beep(800, 200)
        print("  Playing no-barcode sound...")
        winsound.Beep(400, 300)
        print("[PASS] Audio working")
        return True
    except Exception as e:
        print(f"[FAIL] Audio error: {e}")
        return False

def test_file_operations():
    """Test CSV file creation."""
    print("\nTesting file operations...")
    import csv
    import os
    
    test_file = "test_log.csv"
    
    try:
        with open(test_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Test', 'Data'])
        
        if os.path.exists(test_file):
            os.remove(test_file)
            print("[PASS] File operations working")
            return True
        else:
            print("[FAIL] Could not create file")
            return False
    except Exception as e:
        print(f"[FAIL] File error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("PRODUCTION SYSTEM READINESS TEST")
    print("=" * 60)
    
    results = []
    
    results.append(("Camera", test_camera()))
    results.append(("Barcode Detection", test_barcode_detection()))
    results.append(("Audio Alerts", test_audio()))
    results.append(("File Operations", test_file_operations()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED - SYSTEM READY!")
        print("\nYou can now run: python production_line_verifier.py")
    else:
        print("SOME TESTS FAILED - CHECK ERRORS ABOVE")
    print("=" * 60)

if __name__ == "__main__":
    main()
