#!/usr/bin/env python3
"""
Production Line BARCODE (1D) Verification System - HARDWARE ENHANCED
Optimized for traditional barcodes with GPIO buttons, buzzer, and LCD display

Hardware Controls:
- GPIO 22: Capture reference barcode (C Button)
- GPIO 27: Start/Stop production verification (S Button)  
- GPIO 17: Buzzer for audio feedback
- I2C LCD: Status display (address 0x27)

Keyboard Controls (fallback):
- 'c' = Capture reference barcode
- 's' = Start/Stop production verification
- 'q' = Quit system
- 'r' = Reset reference barcode
- 'l' = View logs
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import time
import csv
from datetime import datetime
import os
import subprocess
import threading
import signal
import sys

# GPIO imports with fallback
try:
    from gpiozero import Button, Buzzer
    GPIOZERO_AVAILABLE = True
    print("✓ GPIOZero library available")
except ImportError:
    GPIOZERO_AVAILABLE = False
    print("⚠ GPIOZero not available - using software fallback")

# LCD imports with fallback
try:
    from RPLCD.i2c import CharLCD
    LCD_AVAILABLE = True
    print("✓ RPLCD library available")
except ImportError:
    LCD_AVAILABLE = False
    print("⚠ RPLCD not available - using console output")


class HardwareBarcodeVerifier:
    """Hardware-enhanced barcode verification system with GPIO controls."""
    
    def __init__(self):
        # Hardware configuration
        self.CAPTURE_BTN_PIN = 22    # GPIO 22 - Capture reference
        self.START_BTN_PIN = 27      # GPIO 27 - Start/Stop production
        self.BUZZER_PIN = 17         # GPIO 17 - Buzzer
        self.LCD_ADDRESS = 0x27      # I2C LCD address
        self.LCD_COLS = 16
        self.LCD_ROWS = 2
        
        # Initialize hardware
        self.setup_hardware()
        
        # Barcode verification settings
        self.reference_barcode = None
        self.reference_type = None
        self.production_mode = False
        self.log_file = "production_log_hardware.csv"
        
        # Statistics
        self.stats = {
            'total_scans': 0,
            'passed': 0,
            'mismatched': 0,
            'no_barcode': 0
        }
        
        # Performance tracking
        self.last_scan_time = 0
        self.scan_interval = 1.5  # seconds (for 40 items/min)
        
        # Button state tracking
        self.capture_requested = False
        self.last_capture_btn_state = True
        self.last_start_btn_state = True
        
        # Initialize log file
        self._initialize_log_file()
        
        print("Production Line BARCODE Verification System - HARDWARE ENHANCED")
        print("=" * 70)
        print("HARDWARE CONTROLS:")
        print(f"  GPIO {self.CAPTURE_BTN_PIN} (C Button) - Capture reference barcode")
        print(f"  GPIO {self.START_BTN_PIN} (S Button) - Start/Stop production mode")
        print(f"  GPIO {self.BUZZER_PIN} - Buzzer feedback")
        print(f"  I2C LCD (0x{self.LCD_ADDRESS:02X}) - Status display")
        print("=" * 70)
        print("SUPPORTS ALL TRADITIONAL 1D BARCODES:")
        print("  UPC-A, UPC-E, EAN-13, EAN-8, Code 39, Code 128, ITF, Codabar")
        print("=" * 70)
        print("System initialized successfully!")
        
        # Initial LCD display
        self.display_status("System Ready", "Press C to start")
    
    def setup_hardware(self):
        """Initialize GPIO buttons, buzzer, and LCD display."""
        self.hardware_available = False
        
        # Setup GPIO buttons and buzzer
        if GPIOZERO_AVAILABLE:
            try:
                self.capture_button = Button(self.CAPTURE_BTN_PIN, pull_up=True)
                self.start_button = Button(self.START_BTN_PIN, pull_up=True)
                self.buzzer = Buzzer(self.BUZZER_PIN)
                
                # Set up button event handlers
                self.capture_button.when_pressed = self.handle_capture_button
                self.start_button.when_pressed = self.handle_start_button
                
                self.hardware_available = True
                print(f"✓ GPIO hardware initialized:")
                print(f"  Capture button: GPIO {self.CAPTURE_BTN_PIN}")
                print(f"  Start button: GPIO {self.START_BTN_PIN}")
                print(f"  Buzzer: GPIO {self.BUZZER_PIN}")
                
            except Exception as e:
                print(f"⚠ GPIO setup failed: {e}")
                self.hardware_available = False
        else:
            print("⚠ GPIOZero not available - using software controls only")
        
        # Setup LCD display
        if LCD_AVAILABLE:
            try:
                self.lcd = CharLCD(i2c_expander='PCF8574', address=self.LCD_ADDRESS, 
                                 port=1, cols=self.LCD_COLS, rows=self.LCD_ROWS, 
                                 charmap='A02', auto_linebreaks=True)
                self.lcd.clear()
                self.lcd.write_string("Barcode Verifier")
                self.lcd.cursor_pos = (1, 0)
                self.lcd.write_string("Hardware Ready")
                print(f"✓ I2C LCD initialized on address 0x{self.LCD_ADDRESS:02X}")
            except Exception as e:
                print(f"⚠ LCD setup failed: {e}")
                self.lcd = None
        else:
            self.lcd = None
            print("⚠ LCD not available - using console output")
    
    def display_status(self, line1, line2=""):
        """Display status on LCD and console."""
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
        
        # Console fallback
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {line1} | {line2}")
    
    def play_buzzer_tone(self, tone_type):
        """Play different buzzer tones for different events."""
        if not self.hardware_available:
            # Fallback to speaker-test
            self.play_speaker_tone(tone_type)
            return
        
        def buzzer_thread():
            try:
                if tone_type == 'success':
                    # Short high beep for success
                    self.buzzer.on()
                    time.sleep(0.2)
                    self.buzzer.off()
                elif tone_type == 'mismatch':
                    # Two medium beeps for mismatch
                    for _ in range(2):
                        self.buzzer.on()
                        time.sleep(0.15)
                        self.buzzer.off()
                        time.sleep(0.1)
                elif tone_type == 'no_barcode':
                    # Long low beep for no barcode
                    self.buzzer.on()
                    time.sleep(0.5)
                    self.buzzer.off()
                elif tone_type == 'reference_captured':
                    # Three ascending beeps for reference capture
                    for i in range(3):
                        self.buzzer.on()
                        time.sleep(0.1)
                        self.buzzer.off()
                        time.sleep(0.05)
                elif tone_type == 'start':
                    # Start beep
                    self.buzzer.on()
                    time.sleep(0.3)
                    self.buzzer.off()
                elif tone_type == 'stop':
                    # Stop beep
                    self.buzzer.on()
                    time.sleep(0.2)
                    self.buzzer.off()
                elif tone_type == 'error':
                    # Error pattern - 3 quick beeps
                    for _ in range(3):
                        self.buzzer.on()
                        time.sleep(0.1)
                        self.buzzer.off()
                        time.sleep(0.1)
            except Exception as e:
                print(f"Buzzer error: {e}")
        
        # Run buzzer in separate thread to avoid blocking
        threading.Thread(target=buzzer_thread, daemon=True).start()
    
    def play_speaker_tone(self, tone_type):
        """Fallback speaker tones when hardware buzzer not available."""
        try:
            if tone_type == 'success':
                subprocess.run(['speaker-test', '-t', 'sine', '-f', '1000', '-l', '1'], 
                             capture_output=True, timeout=1)
            elif tone_type == 'mismatch':
                for _ in range(2):
                    subprocess.run(['speaker-test', '-t', 'sine', '-f', '800', '-l', '1'], 
                                 capture_output=True, timeout=1)
                    time.sleep(0.1)
            elif tone_type == 'no_barcode':
                subprocess.run(['speaker-test', '-t', 'sine', '-f', '400', '-l', '1'], 
                             capture_output=True, timeout=1)
            elif tone_type == 'reference_captured':
                for freq in [600, 800, 1000]:
                    subprocess.run(['speaker-test', '-t', 'sine', '-f', str(freq), '-l', '1'], 
                                 capture_output=True, timeout=1)
                    time.sleep(0.05)
        except Exception as e:
            print(f"\\a")  # ASCII bell character as final fallback
    
    def handle_capture_button(self):
        """Handle capture button press."""
        print("\n[CAPTURE] Hardware button pressed - capturing reference...")
        self.capture_requested = True
        self.display_status("Capturing...", "Point at barcode")
    
    def handle_start_button(self):
        """Handle start/stop button press."""
        if not self.reference_barcode:
            self.display_status("No Reference!", "Press C first")
            self.play_buzzer_tone('error')
            print("\n[WARNING] Cannot start production - no reference barcode set!")
        else:
            self.production_mode = not self.production_mode
            if self.production_mode:
                self.display_status("Production ON", f"Ref: {self.reference_barcode[:8]}...")
                self.play_buzzer_tone('start')
                print("\n[START] PRODUCTION MODE STARTED")
                print(f"   Reference: {self.reference_barcode}")
                self.last_scan_time = 0
            else:
                self.display_status("Production OFF", "Press S to start")
                self.play_buzzer_tone('stop')
                print("\n[PAUSE] PRODUCTION MODE PAUSED")
    
    def _initialize_log_file(self):
        """Create CSV log file with headers if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Status', 'Barcode', 'Reference', 'Type'])
            print(f"[OK] Log file created: {self.log_file}")
    
    def log_result(self, status, barcode='', barcode_type=''):
        """Log scan result to CSV file."""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                status,
                barcode,
                self.reference_barcode or '',
                barcode_type
            ])
    
    def preprocess_for_barcode(self, frame):
        """Enhanced preprocessing for barcode detection."""
        results = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results.append(gray)
        
        # Method 1: Otsu's thresholding
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results.append(otsu)
        
        # Method 2: Adaptive thresholding
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                        cv2.THRESH_BINARY, 11, 2)
        results.append(adaptive)
        
        # Method 3: CLAHE enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        clahe_img = clahe.apply(gray)
        results.append(clahe_img)
        
        # Method 4: Sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        results.append(sharpened)
        
        return results
    
    def detect_barcode(self, frame):
        """Enhanced barcode detection for all 1D barcode types."""
        all_barcodes = []
        seen_data = set()
        
        def add_unique_barcode(barcode):
            try:
                data = barcode.data.decode('utf-8')
                if data and data not in seen_data and len(data) > 0:
                    seen_data.add(data)
                    all_barcodes.append(barcode)
                    return True
            except:
                pass
            return False
        
        # STAGE 1: Quick attempts on original and grayscale
        try:
            # Try original color
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # Try grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = pyzbar.decode(gray)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # Try enhanced
            enhanced = cv2.equalizeHist(gray)
            barcodes = pyzbar.decode(enhanced)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
        except:
            pass
        
        # STAGE 2: Try key preprocessing methods
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        try:
            # Otsu's thresholding
            _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            barcodes = pyzbar.decode(otsu)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # Adaptive thresholding
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY, 11, 2)
            barcodes = pyzbar.decode(adaptive)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            clahe_img = clahe.apply(gray)
            barcodes = pyzbar.decode(clahe_img)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
        except:
            pass
        
        return all_barcodes
    
    def capture_reference(self, frame):
        """Capture and store reference barcode from current frame."""
        barcodes = self.detect_barcode(frame)
        
        if not barcodes:
            print("[ERROR] No barcode detected! Please position product correctly and try again.")
            self.display_status("No Barcode!", "Try again")
            self.play_buzzer_tone('no_barcode')
            return False
        
        # Take the first detected barcode as reference
        barcode = barcodes[0]
        self.reference_barcode = barcode.data.decode('utf-8')
        self.reference_type = barcode.type
        
        print("\n" + "=" * 60)
        print("[SUCCESS] REFERENCE BARCODE CAPTURED!")
        print("=" * 60)
        print(f"Barcode: {self.reference_barcode}")
        print(f"Type: {self.reference_type}")
        print("=" * 60)
        print("You can now start production verification (press 'S' or hardware button)")
        print()
        
        self.display_status("Reference Set!", f"{self.reference_type}: {self.reference_barcode[:8]}...")
        self.log_result('REFERENCE_SET', self.reference_barcode, self.reference_type)
        self.play_buzzer_tone('reference_captured')
        
        return True
    
    def verify_product(self, frame):
        """Verify product barcode against reference."""
        if not self.reference_barcode:
            return None
        
        current_time = time.time()
        
        # Check if enough time has passed since last scan (throttling)
        if current_time - self.last_scan_time < self.scan_interval:
            return None
        
        self.last_scan_time = current_time
        
        # Detect barcodes
        barcodes = self.detect_barcode(frame)
        
        self.stats['total_scans'] += 1
        
        if not barcodes:
            # No barcode detected
            self.stats['no_barcode'] += 1
            print(f"\n[ALERT] NO BARCODE DETECTED (Scan #{self.stats['total_scans']})")
            self.display_status("NO BARCODE", f"Scan #{self.stats['total_scans']}")
            self.log_result('NO_BARCODE', '', '')
            self.play_buzzer_tone('no_barcode')
            return 'NO_BARCODE'
        
        # Check first barcode
        barcode = barcodes[0]
        detected_barcode = barcode.data.decode('utf-8')
        detected_type = barcode.type
        
        if detected_barcode == self.reference_barcode:
            # Match - product is correct
            self.stats['passed'] += 1
            print(f"[PASS] (Scan #{self.stats['total_scans']}): {detected_barcode}")
            self.display_status("PASS", f"Scan #{self.stats['total_scans']}")
            self.log_result('PASS', detected_barcode, detected_type)
            self.play_buzzer_tone('success')
            return 'PASS'
        else:
            # Mismatch - wrong product
            self.stats['mismatched'] += 1
            print(f"\n[ALERT] BARCODE MISMATCH (Scan #{self.stats['total_scans']})")
            print(f"   Expected: {self.reference_barcode}")
            print(f"   Found:    {detected_barcode}")
            self.display_status("MISMATCH!", f"Expected: {self.reference_barcode[:8]}...")
            self.log_result('MISMATCH', detected_barcode, detected_type)
            self.play_buzzer_tone('mismatch')
            return 'MISMATCH'
    
    def draw_overlay(self, frame, barcodes):
        """Draw detection overlay on frame."""
        display = frame.copy()
        
        # Draw barcodes
        for barcode in barcodes:
            # Get barcode location
            points = barcode.polygon
            if len(points) == 4:
                pts = [(point.x, point.y) for point in points]
                pts = np.array(pts, dtype=np.int32)
                
                # Determine color based on status
                if self.reference_barcode:
                    detected_data = barcode.data.decode('utf-8')
                    if detected_data == self.reference_barcode:
                        color = (0, 255, 0)  # Green for match
                        status = "MATCH"
                    else:
                        color = (0, 0, 255)  # Red for mismatch
                        status = "MISMATCH"
                else:
                    color = (255, 255, 0)  # Yellow for reference mode
                    status = "DETECTED"
                
                # Draw polygon
                cv2.polylines(display, [pts], True, color, 3)
                
                # Draw barcode data
                x, y = barcode.rect.left, barcode.rect.top
                text = f"{barcode.data.decode('utf-8')} ({barcode.type})"
                cv2.putText(display, text, (x, y - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.putText(display, status, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return display
    
    def draw_status_panel(self, frame):
        """Draw status information panel on frame."""
        display = frame.copy()
        height, width = display.shape[:2]
        
        # Create semi-transparent panel
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 0), (width, 220), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display, 0.3, 0, display)
        
        # Title
        cv2.putText(display, "BARCODE VERIFIER - HARDWARE ENHANCED", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Reference barcode status
        if self.reference_barcode:
            ref_text = f"Reference: {self.reference_barcode} ({self.reference_type})"
            cv2.putText(display, ref_text, (20, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(display, "Reference: NOT SET - Press 'C' or GPIO22 to capture", 
                       (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Production mode status
        if self.production_mode:
            mode_text = "Mode: PRODUCTION ACTIVE"
            mode_color = (0, 255, 0)
        else:
            mode_text = "Mode: STANDBY - Press 'S' or GPIO27 to start"
            mode_color = (255, 255, 0)
        cv2.putText(display, mode_text, (20, 115), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
        
        # Statistics
        stats_text = f"Scans: {self.stats['total_scans']} | Pass: {self.stats['passed']} | Mismatch: {self.stats['mismatched']} | No Barcode: {self.stats['no_barcode']}"
        cv2.putText(display, stats_text, (20, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Performance
        if self.stats['total_scans'] > 0:
            pass_rate = (self.stats['passed'] / self.stats['total_scans']) * 100
            perf_text = f"Pass Rate: {pass_rate:.1f}%"
            cv2.putText(display, perf_text, (20, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Hardware status
        hw_status = "HARDWARE: ON" if self.hardware_available else "HARDWARE: OFF"
        cv2.putText(display, hw_status, (20, 210), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # Controls
        controls_y = height - 30
        if self.hardware_available:
            controls_text = "GPIO22=Capture | GPIO27=Start/Stop | Q=Quit | H=Help"
        else:
            controls_text = "C=Capture | S=Start/Stop | R=Reset | L=Logs | Q=Quit"
        cv2.putText(display, controls_text, (20, controls_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        return display
    
    def print_statistics(self):
        """Print session statistics."""
        print("\n" + "=" * 60)
        print("SESSION STATISTICS")
        print("=" * 60)
        print(f"Total Scans:       {self.stats['total_scans']}")
        print(f"Passed:            {self.stats['passed']}")
        print(f"Mismatched:        {self.stats['mismatched']}")
        print(f"No Barcode:        {self.stats['no_barcode']}")
        if self.stats['total_scans'] > 0:
            pass_rate = (self.stats['passed'] / self.stats['total_scans']) * 100
            print(f"Pass Rate:         {pass_rate:.1f}%")
        print(f"Reference Barcode: {self.reference_barcode or 'Not Set'}")
        print("=" * 60)
    
    def view_logs(self):
        """Display recent log entries."""
        print("\n" + "=" * 60)
        print("RECENT LOG ENTRIES (Last 20)")
        print("=" * 60)
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    print(lines[0].strip())
                    print("-" * 60)
                    for line in lines[-20:]:
                        print(line.strip())
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        print("=" * 60)
    
    def cleanup(self):
        """Clean up hardware resources."""
        try:
            if self.hardware_available:
                if hasattr(self, 'buzzer'):
                    self.buzzer.off()
                    self.buzzer.close()
                if hasattr(self, 'capture_button'):
                    self.capture_button.close()
                if hasattr(self, 'start_button'):
                    self.start_button.close()
            
            if self.lcd:
                self.lcd.clear()
                self.lcd.write_string("System Offline")
                time.sleep(1)
                self.lcd.close()
            
            print("✓ Hardware cleanup completed")
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def run(self):
        """Main loop - run the verification system."""
        print("\n" + "=" * 60)
        print("STARTING CAMERA...")
        print("=" * 60)
        
        # Initialize camera - try different sources including phone camera
        cap = None
        camera_source = None
        
        # Try different camera sources
        camera_sources = [
            # Local USB cameras
            *[i for i in range(10)],
            # DroidCam - Your Samsung A32
            "http://192.168.0.104:4747/video",  # Your DroidCam WiFi IP
            "http://10.142.132.74:4747/video",  # Your DroidCam device IP
            # Alternative DroidCam URLs
            "http://192.168.0.104:4747/mjpegfeed?640x480",
            "http://10.142.132.74:4747/mjpegfeed?640x480",
            # IP Webcam alternatives (in case you switch)
            "http://192.168.0.100:8080/video",
            "http://192.168.0.101:8080/video",
            "http://192.168.0.102:8080/video",
            "http://192.168.0.103:8080/video",
            "http://192.168.0.105:8080/video",
        ]
        
        print("Searching for cameras...")
        for source in camera_sources:
            print(f"Trying camera source: {source}")
            test_cap = cv2.VideoCapture(source)
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                if ret and frame is not None:
                    print(f"[OK] Camera found: {source}")
                    cap = test_cap
                    camera_source = source
                    break
                else:
                    test_cap.release()
            else:
                test_cap.release()
        
        if cap is None:
            print("[ERROR] Could not find any working camera!")
            print("Available video devices:")
            for device in os.listdir('/dev'):
                if device.startswith('video'):
                    print(f"  /dev/{device}")
            print("\n[INFO] To use your phone as camera:")
            print("1. Install 'IP Webcam' app on your phone")
            print("2. Connect phone to same WiFi as Raspberry Pi")
            print("3. Start IP Webcam server on phone")
            print("4. Note the IP address (e.g., 192.168.0.100:8080)")
            print("5. Update the camera_sources list in the code")
            print("\n[INFO] Running in DEMO MODE - No camera available")
            print("This will simulate barcode detection for testing purposes.")
            print("Press 'C' to simulate reference capture, 'S' to start demo mode.")
            self.run_demo_mode()
            return
        
        # Set camera properties for maximum performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Use MJPG for better performance
        
        print("[OK] Camera initialized successfully!")
        self.display_status("Camera Ready", "Press C to start")
        
        print("\nINSTRUCTIONS:")
        if self.hardware_available:
            print("HARDWARE CONTROLS:")
            print(f"1. Press GPIO {self.CAPTURE_BTN_PIN} to capture reference barcode")
            print(f"2. Press GPIO {self.START_BTN_PIN} to start production verification")
            print("3. Buzzer will provide audio feedback")
            print("4. LCD will show status information")
        print("\nKEYBOARD CONTROLS:")
        print("1. Press 'C' to capture reference barcode (do this first!)")
        print("2. Press 'S' to start production verification")
        print("3. Press 'S' again to pause verification")
        print("4. Press 'R' to reset reference barcode")
        print("5. Press 'L' to view logs")
        print("6. Press 'Q' to quit")
        print("\nBARCODE TIPS:")
        print("- Hold barcode flat and steady")
        print("- Ensure good, even lighting")
        print("- Avoid glare and shadows")
        print("- Keep barcode 15-30 cm from camera")
        print("- Try different angles if not detecting\n")
        
        # Set up signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\n[SHUTDOWN] Shutting down system...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[ERROR] Could not read from camera!")
                    break
                
                # Handle capture request from hardware button
                if self.capture_requested:
                    if self.capture_reference(frame):
                        self.capture_requested = False
                    else:
                        self.capture_requested = False
                
                # Always detect barcodes for visual feedback
                # Use lightweight detection for display
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Apply basic enhancement
                enhanced = cv2.equalizeHist(gray)
                
                # Try multiple quick methods for display
                barcodes = pyzbar.decode(frame)
                if not barcodes:
                    barcodes = pyzbar.decode(gray)
                if not barcodes:
                    barcodes = pyzbar.decode(enhanced)
                
                # Draw barcode overlays
                if barcodes:
                    frame = self.draw_overlay(frame, barcodes)
                
                # Draw status panel
                display_frame = self.draw_status_panel(frame)
                
                # Production mode - automatic verification
                if self.production_mode and self.reference_barcode:
                    self.verify_product(frame)
                
                # Display frame
                cv2.imshow('Barcode Verifier - Hardware Enhanced', display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n[SHUTDOWN] Shutting down system...")
                    break
                
                elif key == ord('c'):
                    print("\n[CAPTURE] Capturing reference barcode...")
                    self.capture_reference(frame)
                
                elif key == ord('s'):
                    self.handle_start_button()
                
                elif key == ord('r'):
                    print("\n[RESET] Resetting reference barcode...")
                    self.reference_barcode = None
                    self.reference_type = None
                    self.production_mode = False
                    self.display_status("Reference Reset", "Press C to set new")
                    print("[OK] Reference barcode cleared. Press 'C' to set new reference.")
                
                elif key == ord('l'):
                    self.view_logs()
                
                elif key == ord('h'):
                    print("\n" + "=" * 60)
                    print("HELP - CONTROLS")
                    print("=" * 60)
                    if self.hardware_available:
                        print("HARDWARE CONTROLS:")
                        print(f"GPIO {self.CAPTURE_BTN_PIN} - Capture reference barcode")
                        print(f"GPIO {self.START_BTN_PIN} - Start/Stop production verification")
                        print(f"GPIO {self.BUZZER_PIN} - Buzzer feedback")
                        print("I2C LCD - Status display")
                        print("=" * 60)
                    print("KEYBOARD CONTROLS:")
                    print("C - Capture reference barcode")
                    print("S - Start/Stop production verification")
                    print("R - Reset reference barcode")
                    print("L - View recent logs")
                    print("H - Show this help")
                    print("Q - Quit system")
                    print("\nBARCODE DETECTION TIPS:")
                    print("- Use good, even lighting (avoid shadows)")
                    print("- Hold barcode flat and parallel to camera")
                    print("- Keep barcode at 15-30 cm distance")
                    print("- Avoid glare on barcode surface")
                    print("- Try rotating slightly if not detecting")
                    print("=" * 60)
        
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] System interrupted by user...")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
        finally:
            # Cleanup
            self.print_statistics()
            cap.release()
            cv2.destroyAllWindows()
            self.cleanup()
            
            print("\n[OK] System shutdown complete!")
            print(f"Full logs saved to: {self.log_file}")
    
    def run_demo_mode(self):
        """Run in demo mode when no camera is available."""
        print("\n" + "=" * 60)
        print("DEMO MODE - BARCODE VERIFICATION SYSTEM")
        print("=" * 60)
        print("No camera detected. Running in simulation mode.")
        print("\nDemo barcodes available:")
        print("1. 1234567890123 (EAN13)")
        print("2. 9876543210987 (EAN13 - different)")
        print("3. NO_BARCODE (simulate missing barcode)")
        print("\nControls:")
        if self.hardware_available:
            print(f"GPIO {self.CAPTURE_BTN_PIN} - Simulate reference capture")
            print(f"GPIO {self.START_BTN_PIN} - Start/Stop demo verification")
        print("C - Simulate reference capture")
        print("S - Start/Stop demo verification")
        print("R - Reset reference")
        print("L - View logs")
        print("Q - Quit")
        print("=" * 60)
        
        demo_barcodes = [
            "1234567890123",
            "9876543210987", 
            "NO_BARCODE"
        ]
        current_demo_index = 0
        
        # Set up signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\n[SHUTDOWN] Shutting down demo mode...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while True:
                print(f"\nCurrent demo barcode: {demo_barcodes[current_demo_index]}")
                print("Commands: C=Capture Ref, S=Start Demo, R=Reset, L=Logs, Q=Quit, N=Next Barcode")
                
                try:
                    command = input("Enter command: ").strip().lower()
                    
                    if command == 'q':
                        break
                    elif command == 'c':
                        if demo_barcodes[current_demo_index] != "NO_BARCODE":
                            self.reference_barcode = demo_barcodes[current_demo_index]
                            self.reference_type = "EAN13"
                            print(f"\n[SUCCESS] REFERENCE CAPTURED: {self.reference_barcode}")
                            self.display_status("Reference Set!", f"Demo: {self.reference_barcode}")
                            self.log_result('REFERENCE_SET', self.reference_barcode, self.reference_type)
                            self.play_buzzer_tone('reference_captured')
                        else:
                            print("[ERROR] Cannot capture reference from NO_BARCODE")
                            self.play_buzzer_tone('no_barcode')
                    elif command == 's':
                        if not self.reference_barcode:
                            print("[WARNING] No reference set! Press 'C' first.")
                            self.play_buzzer_tone('no_barcode')
                        else:
                            self.production_mode = not self.production_mode
                            if self.production_mode:
                                print(f"\n[START] DEMO PRODUCTION MODE STARTED")
                                print(f"Reference: {self.reference_barcode}")
                                self.display_status("Demo Production ON", f"Ref: {self.reference_barcode}")
                                self.play_buzzer_tone('start')
                            else:
                                print("\n[PAUSE] DEMO PRODUCTION MODE PAUSED")
                                self.display_status("Demo Production OFF", "Press S to start")
                                self.play_buzzer_tone('stop')
                    elif command == 'r':
                        self.reference_barcode = None
                        self.reference_type = None
                        self.production_mode = False
                        self.display_status("Reference Reset", "Press C to set new")
                        print("[OK] Reference reset")
                    elif command == 'l':
                        self.view_logs()
                    elif command == 'n':
                        current_demo_index = (current_demo_index + 1) % len(demo_barcodes)
                        print(f"Switched to: {demo_barcodes[current_demo_index]}")
                    else:
                        print("Invalid command. Use: C, S, R, L, Q, N")
                    
                    # Simulate production verification if in production mode
                    if self.production_mode and self.reference_barcode:
                        current_barcode = demo_barcodes[current_demo_index]
                        if current_barcode == "NO_BARCODE":
                            self.stats['total_scans'] += 1
                            self.stats['no_barcode'] += 1
                            print(f"[ALERT] NO BARCODE DETECTED (Demo Scan #{self.stats['total_scans']})")
                            self.display_status("NO BARCODE", f"Demo Scan #{self.stats['total_scans']}")
                            self.log_result('NO_BARCODE', '', '')
                            self.play_buzzer_tone('no_barcode')
                        elif current_barcode == self.reference_barcode:
                            self.stats['total_scans'] += 1
                            self.stats['passed'] += 1
                            print(f"[PASS] (Demo Scan #{self.stats['total_scans']}): {current_barcode}")
                            self.display_status("PASS", f"Demo Scan #{self.stats['total_scans']}")
                            self.log_result('PASS', current_barcode, 'EAN13')
                            self.play_buzzer_tone('success')
                        else:
                            self.stats['total_scans'] += 1
                            self.stats['mismatched'] += 1
                            print(f"[ALERT] BARCODE MISMATCH (Demo Scan #{self.stats['total_scans']})")
                            print(f"   Expected: {self.reference_barcode}")
                            print(f"   Found:    {current_barcode}")
                            self.display_status("MISMATCH!", f"Expected: {self.reference_barcode}")
                            self.log_result('MISMATCH', current_barcode, 'EAN13')
                            self.play_buzzer_tone('mismatch')
                        
                        time.sleep(1)  # Simulate scan interval
                        
                except KeyboardInterrupt:
                    break
        
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Demo mode interrupted by user...")
        finally:
            self.print_statistics()
            self.cleanup()


def main():
    """Entry point."""
    verifier = HardwareBarcodeVerifier()
    verifier.run()


if __name__ == "__main__":
    main()
