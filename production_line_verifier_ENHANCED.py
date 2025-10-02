#!/usr/bin/env python3
"""
Production Line Barcode Verification System - ENHANCED HARDWARE
Enhanced with modern gpiozero library, automatic button controls, and improved buzzer feedback
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import csv
import time
import threading
import subprocess
from datetime import datetime

# Modern GPIO library
from gpiozero import Button, Buzzer
from RPLCD.i2c import CharLCD
import warnings
warnings.filterwarnings("ignore")

class EnhancedBarcodeVerifier:
    def __init__(self):
        # GPIO Pin Configuration (matching our test hardware)
        self.BUZZER_PIN = 17      # Buzzer on GPIO 17
        self.START_BTN_PIN = 22   # Start/Stop button on GPIO 22
        self.CAPTURE_BTN_PIN = 27 # Capture reference button on GPIO 27
        
        # LCD Configuration (I2C on pins 2,3 - SDA,SCL)
        self.LCD_ADDRESS = 0x27   # Common I2C address for LCD
        self.LCD_COLS = 16
        self.LCD_ROWS = 2
        
        # Initialize hardware
        self.setup_hardware()
        self.setup_lcd()
        
        # Barcode verification settings
        self.reference_barcode = None
        self.reference_type = None
        self.production_mode = False
        self.scan_interval = 1.5  # seconds
        self.last_scan_time = 0
        
        # Statistics
        self.total_scans = 0
        self.passed_scans = 0
        self.mismatched_scans = 0
        self.no_barcode_scans = 0
        
        # Logging
        self.log_file = "production_log_enhanced.csv"
        self.setup_logging()
        
        # Button state tracking
        self.hardware_available = False
        self.capture_requested = False
        
        print("Enhanced Hardware Barcode Verification System Initialized!")
        self.display_status("System Ready", "Press C to start")
    
    def setup_hardware(self):
        """Initialize GPIO pins using modern gpiozero library"""
        try:
            # Initialize buzzer
            self.buzzer = Buzzer(self.BUZZER_PIN)
            
            # Initialize buttons with pull-up resistors
            self.start_button = Button(self.START_BTN_PIN, pull_up=True)
            self.capture_button = Button(self.CAPTURE_BTN_PIN, pull_up=True)
            
            # Set up button event handlers
            self.start_button.when_pressed = self.handle_start_button
            self.capture_button.when_pressed = self.handle_capture_button
            
            self.hardware_available = True
            print(f"✓ Hardware initialized successfully:")
            print(f"  Buzzer: GPIO {self.BUZZER_PIN}")
            print(f"  Start Button: GPIO {self.START_BTN_PIN}")
            print(f"  Capture Button: GPIO {self.CAPTURE_BTN_PIN}")
            
        except Exception as e:
            self.hardware_available = False
            print(f"Hardware setup failed: {e}")
            print("Running in software-only mode")
    
    def setup_lcd(self):
        """Initialize I2C LCD display"""
        try:
            self.lcd = CharLCD('PCF8574', self.LCD_ADDRESS, cols=self.LCD_COLS, rows=self.LCD_ROWS)
            self.lcd.clear()
            self.lcd.cursor_pos = (0, 0)
            self.lcd.write_string("Barcode Verifier")
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string("Enhanced Ready")
            print(f"✓ LCD initialized on I2C address 0x{self.LCD_ADDRESS:02X}")
        except Exception as e:
            print(f"LCD initialization failed: {e}")
            self.lcd = None
    
    def display_status(self, line1, line2=""):
        """Display status on LCD"""
        if self.lcd:
            try:
                self.lcd.clear()
                self.lcd.cursor_pos = (0, 0)
                self.lcd.write_string(line1[:self.LCD_COLS])
                if line2:
                    self.lcd.cursor_pos = (1, 0)
                    self.lcd.write_string(line2[:self.LCD_COLS])
            except Exception as e:
                print(f"LCD display error: {e}")
    
    def play_buzzer_tone(self, tone_type):
        """Play different buzzer tones for different actions"""
        def buzzer_thread():
            if tone_type == "reference_captured":
                # 3 short beeps
                for _ in range(3):
                    self.buzzer.on()
                    time.sleep(0.2)
                    self.buzzer.off()
                    time.sleep(0.1)
            elif tone_type == "pass":
                # Short beep
                self.buzzer.on()
                time.sleep(0.3)
                self.buzzer.off()
            elif tone_type == "mismatch":
                # Double beep
                for _ in range(2):
                    self.buzzer.on()
                    time.sleep(0.2)
                    self.buzzer.off()
                    time.sleep(0.1)
            elif tone_type == "start":
                # Long beep
                self.buzzer.on()
                time.sleep(0.5)
                self.buzzer.off()
            elif tone_type == "stop":
                # Two short beeps
                for _ in range(2):
                    self.buzzer.on()
                    time.sleep(0.1)
                    self.buzzer.off()
                    time.sleep(0.1)
            elif tone_type == "error":
                # Rapid beeping
                for _ in range(5):
                    self.buzzer.on()
                    time.sleep(0.1)
                    self.buzzer.off()
                    time.sleep(0.1)
        
        if self.hardware_available:
            threading.Thread(target=buzzer_thread, daemon=True).start()
    
    def handle_start_button(self):
        """Handle start/stop button press"""
        if not self.reference_barcode:
            self.display_status("No Reference!", "Press C first")
            self.play_buzzer_tone("error")
            print("\n[WARNING] Cannot start production - no reference barcode set!")
        else:
            self.production_mode = not self.production_mode
            if self.production_mode:
                self.display_status("Production ON", f"Ref: {self.reference_barcode[:8]}...")
                self.play_buzzer_tone("start")
                print("\n[START] PRODUCTION MODE STARTED")
                self.last_scan_time = 0
            else:
                self.display_status("Production OFF", "Press S to start")
                self.play_buzzer_tone("stop")
                print("\n[PAUSE] PRODUCTION MODE PAUSED")
    
    def handle_capture_button(self):
        """Handle capture reference button press"""
        print("\n[CAPTURE] Capturing reference barcode...")
        self.display_status("Capturing...", "Point at barcode")
        self.capture_requested = True
        self.play_buzzer_tone("reference_captured")
    
    def setup_logging(self):
        """Setup CSV logging"""
        try:
            with open(self.log_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'Action', 'Barcode', 'Type', 'Result', 'Details'])
        except Exception as e:
            print(f"Logging setup error: {e}")
    
    def log_event(self, action, barcode=None, barcode_type=None, result=None, details=""):
        """Log event to CSV file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, action, barcode, barcode_type, result, details])
        except Exception as e:
            print(f"Logging error: {e}")
    
    def detect_barcodes(self, frame):
        """Detect barcodes in frame"""
        barcodes = pyzbar.decode(frame)
        return barcodes
    
    def draw_overlay(self, frame, barcodes):
        """Draw barcode detection overlay"""
        for barcode in barcodes:
            # Extract barcode data and type
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            # Draw rectangle around barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw barcode data and type
            text = f"{barcode_type}: {barcode_data}"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame
    
    def draw_status_panel(self, frame):
        """Draw status panel on frame"""
        height, width = frame.shape[:2]
        
        # Create status panel
        panel_height = 120
        panel = np.zeros((panel_height, width, 3), dtype=np.uint8)
        
        # Status text
        status_text = "PRODUCTION ON" if self.production_mode else "PRODUCTION OFF"
        ref_text = f"REF: {self.reference_barcode[:12]}..." if self.reference_barcode else "REF: Not Set"
        
        # Color coding
        color = (0, 255, 0) if self.production_mode else (0, 0, 255)
        
        cv2.putText(panel, status_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(panel, ref_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Statistics
        stats_text = f"Scans: {self.total_scans} | Pass: {self.passed_scans} | Fail: {self.mismatched_scans}"
        cv2.putText(panel, stats_text, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Hardware status
        hw_text = f"HW: {'ON' if self.hardware_available else 'OFF'} | Buttons: GPIO22,27 | Buzzer: GPIO17"
        cv2.putText(panel, hw_text, (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Combine frame and panel
        combined = np.vstack([frame, panel])
        return combined
    
    def capture_reference(self, frame):
        """Capture reference barcode from frame"""
        barcodes = self.detect_barcodes(frame)
        
        if barcodes:
            barcode = barcodes[0]  # Take first barcode found
            self.reference_barcode = barcode.data.decode('utf-8')
            self.reference_type = barcode.type
            
            self.display_status("Reference Set!", f"Type: {self.reference_type}")
            self.play_buzzer_tone("reference_captured")
            
            print(f"\n[SUCCESS] Reference barcode captured:")
            print(f"  Type: {self.reference_type}")
            print(f"  Data: {self.reference_barcode}")
            
            self.log_event("reference_captured", self.reference_barcode, self.reference_type, "success")
            return True
        else:
            self.display_status("No Barcode Found", "Try again")
            self.play_buzzer_tone("error")
            print("\n[ERROR] No barcode detected in frame")
            return False
    
    def verify_product(self, frame):
        """Verify product barcode against reference"""
        current_time = time.time()
        if current_time - self.last_scan_time < self.scan_interval:
            return
        
        barcodes = self.detect_barcodes(frame)
        self.last_scan_time = current_time
        
        if barcodes:
            barcode = barcodes[0]
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            self.total_scans += 1
            
            if barcode_data == self.reference_barcode:
                # Match found
                self.passed_scans += 1
                self.display_status("PASS", f"Match: {barcode_data[:8]}...")
                self.play_buzzer_tone("pass")
                print(f"\n[PASS] Product verified: {barcode_data}")
                self.log_event("product_verified", barcode_data, barcode_type, "pass")
            else:
                # Mismatch
                self.mismatched_scans += 1
                self.display_status("FAIL", f"Mismatch detected")
                self.play_buzzer_tone("mismatch")
                print(f"\n[FAIL] Mismatch detected:")
                print(f"  Expected: {self.reference_barcode}")
                print(f"  Found: {barcode_data}")
                self.log_event("product_verified", barcode_data, barcode_type, "mismatch", 
                             f"Expected: {self.reference_barcode}")
        else:
            self.no_barcode_scans += 1
            print(f"\n[INFO] No barcode detected (scan {self.total_scans + 1})")
    
    def print_statistics(self):
        """Print session statistics"""
        print("\n" + "=" * 60)
        print("SESSION STATISTICS")
        print("=" * 60)
        print(f"Total Scans:       {self.total_scans}")
        print(f"Passed:            {self.passed_scans}")
        print(f"Mismatched:        {self.mismatched_scans}")
        print(f"No Barcode:        {self.no_barcode_scans}")
        
        if self.total_scans > 0:
            pass_rate = (self.passed_scans / self.total_scans) * 100
            print(f"Pass Rate:         {pass_rate:.1f}%")
        
        print(f"Reference Barcode: {self.reference_barcode or 'Not Set'}")
        print("=" * 60)
    
    def cleanup(self):
        """Cleanup hardware resources"""
        try:
            if hasattr(self, 'lcd') and self.lcd:
                self.lcd.clear()
                self.lcd.close()
            if self.hardware_available:
                self.buzzer.off()
                self.buzzer.close()
                self.start_button.close()
                self.capture_button.close()
            print("Hardware cleanup completed.")
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def run(self):
        """Main application loop"""
        print("=" * 60)
        print("Production Line BARCODE Verification System - ENHANCED HARDWARE")
        print("=" * 60)
        print("HARDWARE CONTROLS:")
        print("  GPIO 27 (C Button) - Capture reference barcode")
        print("  GPIO 22 (S Button) - Start/Stop production mode")
        print("  GPIO 17 - Buzzer feedback")
        print("  LCD I2C - Status display")
        print("=" * 60)
        print("KEYBOARD CONTROLS:")
        print("  Q - Quit system")
        print("  H - Show help")
        print("=" * 60)
        
        # Initialize LCD
        self.setup_lcd()
        
        # Initialize camera
        cap = None
        camera_sources = [
            *[i for i in range(10)],
            "http://192.168.0.104:4747/video",  # Your DroidCam
            "http://192.168.0.104:4747/mjpegfeed?640x480",  # Alternative DroidCam URL
            "http://10.142.132.74:4747/video",  # Alternative DroidCam IP
            "http://10.142.132.74:4747/mjpegfeed?640x480",  # Alternative DroidCam URL
        ]
        
        print("Searching for cameras...")
        for source in camera_sources:
            print(f"Trying camera source: {source}")
            test_cap = cv2.VideoCapture(source)
            if test_cap.isOpened():
                # Set buffer size to reduce latency
                test_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                ret, frame = test_cap.read()
                if ret and frame is not None:
                    cap = test_cap
                    print(f"[OK] Camera found: {source}")
                    print(f"[OK] Frame size: {frame.shape[1]}x{frame.shape[0]}")
                    break
                else:
                    print(f"[SKIP] Camera opened but no frame: {source}")
                    test_cap.release()
            else:
                print(f"[SKIP] Camera failed to open: {source}")
                test_cap.release()
        
        if not cap:
            print("[ERROR] No camera found!")
            self.display_status("No Camera!", "Check connection")
            return
        
        print("[OK] Camera initialized successfully!")
        self.display_status("Camera Ready", "Press C to start")
        
        # Main loop
        try:
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print(f"Failed to read from camera (attempt {frame_count + 1})")
                    frame_count += 1
                    if frame_count > 10:  # Try 10 times before giving up
                        print("Camera stream lost, exiting...")
                        break
                    time.sleep(0.1)
                    continue
                
                frame_count = 0  # Reset counter on successful read
                
                # Handle capture request from button
                if self.capture_requested:
                    if self.capture_reference(frame):
                        self.capture_requested = False
                    else:
                        self.capture_requested = False
                
                # Detect barcodes
                barcodes = self.detect_barcodes(frame)
                
                # Draw overlays
                if barcodes:
                    frame = self.draw_overlay(frame, barcodes)
                
                # Draw status panel
                display_frame = self.draw_status_panel(frame)
                
                # Production mode verification
                if self.production_mode and self.reference_barcode:
                    self.verify_product(frame)
                
                # Display frame
                cv2.imshow('Barcode Verifier - Enhanced Hardware', display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n[SHUTDOWN] Shutting down system...")
                    break
                elif key == ord('h'):
                    print("\n" + "=" * 60)
                    print("HELP - HARDWARE CONTROLS")
                    print("=" * 60)
                    print("GPIO 27 (C Button) - Capture reference barcode")
                    print("GPIO 22 (S Button) - Start/Stop production mode")
                    print("GPIO 17 - Buzzer feedback")
                    print("LCD I2C - Status display")
                    print("=" * 60)
                    print("KEYBOARD CONTROLS:")
                    print("Q - Quit system")
                    print("H - Show this help")
                    print("=" * 60)
                elif key == ord('c'):
                    self.capture_requested = True
                elif key == ord('s'):
                    self.handle_start_button()
        
        except KeyboardInterrupt:
            print("\nSystem interrupted by user.")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            self.print_statistics()
            self.cleanup()
            print(f"\n[OK] System shutdown complete!")
            print(f"Full logs saved to: {self.log_file}")

if __name__ == "__main__":
    verifier = EnhancedBarcodeVerifier()
    verifier.run()
