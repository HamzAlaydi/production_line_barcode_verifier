#!/usr/bin/env python3
"""
Production Line Barcode Verification System - HARDWARE ENHANCED
Enhanced with GPIO buzzer, buttons, and LCD display
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import csv
import time
import threading
import subprocess
try:
    import RPi.GPIO as GPIO
    GPIO_LIBRARY = "RPi.GPIO"
except ImportError:
    try:
        import RPi.lgpio as GPIO
        GPIO_LIBRARY = "RPi.lgpio"
    except ImportError:
        GPIO = None
        GPIO_LIBRARY = None
from RPLCD.i2c import CharLCD
import warnings
warnings.filterwarnings("ignore")

class HardwareBarcodeVerifier:
    def __init__(self):
        # GPIO Pin Configuration
        self.BUZZER_PIN = 17      # Buzzer on GPIO 17
        self.START_BTN_PIN = 22   # Start/Stop button on GPIO 22
        self.CAPTURE_BTN_PIN = 27 # Capture reference button on GPIO 27
        
        # LCD Configuration (I2C on pins 2,3 - SDA,SCL)
        self.LCD_ADDRESS = 0x27   # Common I2C address for LCD
        self.LCD_COLS = 16
        self.LCD_ROWS = 2
        
        # Initialize GPIO
        self.setup_gpio()
        
        # Initialize LCD
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
        self.log_file = "production_log_hardware.csv"
        self.setup_logging()
        
        # Button state tracking
        self.gpio_available = False
        self.last_start_btn_state = GPIO.HIGH
        self.last_capture_btn_state = GPIO.HIGH
        
        print("Hardware-Enhanced Barcode Verification System Initialized!")
        self.display_status("System Ready", "Press C to start")
    
    def setup_gpio(self):
        """Initialize GPIO pins for buzzer and buttons"""
        if GPIO is None:
            self.gpio_available = False
            print("No GPIO library available - running in software-only mode")
            return
            
        try:
            if GPIO_LIBRARY == "RPi.GPIO":
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                
                # Setup buzzer pin
                GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
                GPIO.output(self.BUZZER_PIN, GPIO.LOW)
                
                # Setup button pins with pull-up resistors
                GPIO.setup(self.START_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(self.CAPTURE_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                
            elif GPIO_LIBRARY == "RPi.lgpio":
                # For lgpio library
                self.gpio_handle = GPIO.gpiochip_open(0)
                GPIO.gpio_claim_output(self.gpio_handle, self.BUZZER_PIN, 0)
                GPIO.gpio_claim_input(self.gpio_handle, self.START_BTN_PIN, GPIO.SET_PULL_UP)
                GPIO.gpio_claim_input(self.gpio_handle, self.CAPTURE_BTN_PIN, GPIO.SET_PULL_UP)
            
            self.gpio_available = True
            print(f"GPIO pins configured using {GPIO_LIBRARY}:")
            print(f"  Buzzer: GPIO {self.BUZZER_PIN}")
            print(f"  Start Button: GPIO {self.START_BTN_PIN} (PUD_UP enabled)")
            print(f"  Capture Button: GPIO {self.CAPTURE_BTN_PIN} (PUD_UP enabled)")
            print("  Button wiring: GPIO → Button Pin 1, GND → Button Pin 2")
            print("  No external resistors needed!")
        except Exception as e:
            self.gpio_available = False
            print(f"GPIO setup failed: {e}")
            print("Running in software-only mode (keyboard controls only)")
    
    def setup_lcd(self):
        """Initialize I2C LCD display"""
        try:
            self.lcd = CharLCD('PCF8574', self.LCD_ADDRESS, cols=self.LCD_COLS, rows=self.LCD_ROWS)
            self.lcd.clear()
            self.lcd.cursor_pos = (0, 0)
            self.lcd.write_string("Barcode Verifier")
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string("Hardware Ready")
            print(f"LCD initialized on I2C address 0x{self.LCD_ADDRESS:02X}")
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
                    self.buzzer_beep(0, 0.2)  # 0 frequency = simple ON/OFF
                    time.sleep(0.1)
            elif tone_type == "pass":
                # Short beep
                self.buzzer_beep(0, 0.3)
            elif tone_type == "mismatch":
                # Double beep
                self.buzzer_beep(0, 0.2)
                time.sleep(0.1)
                self.buzzer_beep(0, 0.2)
            elif tone_type == "no_barcode":
                # Long beep
                self.buzzer_beep(0, 0.8)
            elif tone_type == "error":
                # Error beep pattern - 3 quick beeps
                for _ in range(3):
                    self.buzzer_beep(0, 0.1)
                    time.sleep(0.1)
            elif tone_type == "start":
                # Start beep
                self.buzzer_beep(0, 0.5)
            elif tone_type == "stop":
                # Stop beep
                self.buzzer_beep(0, 0.3)
        
        # Run buzzer in separate thread to avoid blocking
        threading.Thread(target=buzzer_thread, daemon=True).start()
    
    def buzzer_beep(self, frequency, duration):
        """Generate buzzer beep using simple ON/OFF"""
        if not self.gpio_available:
            # Fallback to speaker-test if GPIO not available
            try:
                subprocess.run(['speaker-test', '-t', 'sine', '-f', '1000', '-l', '1'], 
                             capture_output=True, timeout=duration+1)
            except:
                pass
            return
            
        try:
            if GPIO_LIBRARY == "RPi.GPIO":
                # For active buzzer: HIGH = ON, LOW = OFF
                GPIO.output(self.BUZZER_PIN, GPIO.HIGH)
                time.sleep(duration)
                GPIO.output(self.BUZZER_PIN, GPIO.LOW)
            elif GPIO_LIBRARY == "RPi.lgpio":
                # For lgpio library
                GPIO.gpio_write(self.gpio_handle, self.BUZZER_PIN, 1)
                time.sleep(duration)
                GPIO.gpio_write(self.gpio_handle, self.BUZZER_PIN, 0)
        except Exception as e:
            print(f"Buzzer error: {e}")
    
    def check_buttons(self):
        """Check button states and handle presses"""
        if not self.gpio_available:
            return
            
        try:
            if GPIO_LIBRARY == "RPi.GPIO":
                # Check start/stop button (GPIO 22)
                start_btn_state = GPIO.input(self.START_BTN_PIN)
                if start_btn_state == GPIO.LOW and self.last_start_btn_state == GPIO.HIGH:
                    # Button pressed (falling edge)
                    self.handle_start_button()
                    time.sleep(0.1)  # Debounce
                self.last_start_btn_state = start_btn_state
                
                # Check capture button (GPIO 27)
                capture_btn_state = GPIO.input(self.CAPTURE_BTN_PIN)
                if capture_btn_state == GPIO.LOW and self.last_capture_btn_state == GPIO.HIGH:
                    # Button pressed (falling edge)
                    self.handle_capture_button()
                    time.sleep(0.1)  # Debounce
                self.last_capture_btn_state = capture_btn_state
                
            elif GPIO_LIBRARY == "RPi.lgpio":
                # Check start/stop button (GPIO 22)
                start_btn_state = GPIO.gpio_read(self.gpio_handle, self.START_BTN_PIN)
                if start_btn_state == 0 and self.last_start_btn_state == 1:
                    # Button pressed (falling edge)
                    self.handle_start_button()
                    time.sleep(0.1)  # Debounce
                self.last_start_btn_state = start_btn_state
                
                # Check capture button (GPIO 27)
                capture_btn_state = GPIO.gpio_read(self.gpio_handle, self.CAPTURE_BTN_PIN)
                if capture_btn_state == 0 and self.last_capture_btn_state == 1:
                    # Button pressed (falling edge)
                    self.handle_capture_button()
                    time.sleep(0.1)  # Debounce
                self.last_capture_btn_state = capture_btn_state
                
        except Exception as e:
            print(f"Button check error: {e}")
    
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
        # Note: We'll capture the reference in the main loop when this button is pressed
    
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
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
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
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def draw_status_panel(self, frame):
        """Draw status information on frame"""
        # Create status panel
        panel_height = 120
        panel = np.zeros((panel_height, frame.shape[1], 3), dtype=np.uint8)
        
        # Status text
        status_text = "READY" if not self.production_mode else "PRODUCTION"
        color = (0, 255, 0) if not self.production_mode else (0, 0, 255)
        
        cv2.putText(panel, f"Status: {status_text}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        if self.reference_barcode:
            ref_text = f"Ref: {self.reference_barcode[:20]}..."
            cv2.putText(panel, ref_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Statistics
        stats_text = f"Scans: {self.total_scans} | Pass: {self.passed_scans} | Fail: {self.mismatched_scans}"
        cv2.putText(panel, stats_text, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Controls
        if self.gpio_available:
            controls_text = "HARDWARE: GPIO27=Capture, GPIO22=Start/Stop | Keyboard: Q=Quit"
        else:
            controls_text = "KEYBOARD: C=Capture, S=Start/Stop, Q=Quit, H=Help"
        cv2.putText(panel, controls_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Combine frame and panel
        display_frame = np.vstack([frame, panel])
        return display_frame
    
    def capture_reference(self, frame):
        """Capture reference barcode"""
        barcodes = self.detect_barcodes(frame)
        
        if barcodes:
            barcode = barcodes[0]  # Use first detected barcode
            self.reference_barcode = barcode.data.decode('utf-8')
            self.reference_type = barcode.type
            
            self.display_status("Reference Set!", f"{self.reference_type}: {self.reference_barcode[:8]}...")
            self.play_buzzer_tone("reference_captured")
            self.log_event("REFERENCE_CAPTURED", self.reference_barcode, self.reference_type, "SUCCESS")
            
            print(f"\n[SUCCESS] REFERENCE BARCODE CAPTURED!")
            print(f"Barcode: {self.reference_barcode}")
            print(f"Type: {self.reference_type}")
            return True
        else:
            self.display_status("No Barcode!", "Try again")
            self.play_buzzer_tone("error")
            print("[ERROR] No barcode detected! Please position product correctly and try again.")
            return False
    
    def verify_product(self, frame):
        """Verify product against reference barcode"""
        current_time = time.time()
        if current_time - self.last_scan_time < self.scan_interval:
            return
        
        self.last_scan_time = current_time
        barcodes = self.detect_barcodes(frame)
        self.total_scans += 1
        
        if barcodes:
            barcode = barcodes[0]
            detected_barcode = barcode.data.decode('utf-8')
            detected_type = barcode.type
            
            if detected_barcode == self.reference_barcode:
                # PASS
                self.passed_scans += 1
                self.display_status("PASS", f"Scan #{self.total_scans}")
                self.play_buzzer_tone("pass")
                self.log_event("VERIFICATION", detected_barcode, detected_type, "PASS")
                print(f"[PASS] (Scan #{self.total_scans}): {detected_barcode}")
            else:
                # MISMATCH
                self.mismatched_scans += 1
                self.display_status("MISMATCH!", f"Expected: {self.reference_barcode[:8]}...")
                self.play_buzzer_tone("mismatch")
                self.log_event("VERIFICATION", detected_barcode, detected_type, "MISMATCH", 
                             f"Expected: {self.reference_barcode}")
                print(f"[MISMATCH] (Scan #{self.total_scans})")
                print(f"   Expected: {self.reference_barcode}")
                print(f"   Found:    {detected_barcode}")
        else:
            # NO BARCODE
            self.no_barcode_scans += 1
            self.display_status("NO BARCODE", f"Scan #{self.total_scans}")
            self.play_buzzer_tone("no_barcode")
            self.log_event("VERIFICATION", None, None, "NO_BARCODE")
            print(f"[NO BARCODE] (Scan #{self.total_scans})")
    
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
        """Cleanup GPIO and LCD"""
        try:
            if hasattr(self, 'lcd') and self.lcd:
                self.lcd.clear()
                self.lcd.close()
            if self.gpio_available and GPIO is not None:
                if GPIO_LIBRARY == "RPi.GPIO":
                    GPIO.cleanup()
                elif GPIO_LIBRARY == "RPi.lgpio":
                    GPIO.gpiochip_close(self.gpio_handle)
            print("Hardware cleanup completed.")
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def run(self):
        """Main application loop"""
        print("=" * 60)
        print("Production Line BARCODE Verification System - HARDWARE ENHANCED")
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
        capture_requested = False
        
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
                
                # Check hardware buttons (priority over keyboard)
                self.check_buttons()
                
                # Handle capture request from button
                if capture_requested:
                    if self.capture_reference(frame):
                        capture_requested = False
                    else:
                        capture_requested = False
                
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
                cv2.imshow('Barcode Verifier - Hardware Enhanced', display_frame)
                
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
                    capture_requested = True
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
    verifier = HardwareBarcodeVerifier()
    verifier.run()
