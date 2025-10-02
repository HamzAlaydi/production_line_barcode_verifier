#!/usr/bin/env python3
"""
Production Line Demo - Shows how the enhanced system works
"""

from gpiozero import Button, Buzzer
from RPLCD.i2c import CharLCD
import time
import threading

# GPIO pins
BUZZER_PIN = 17
START_BTN_PIN = 22
CAPTURE_BTN_PIN = 27
LCD_ADDRESS = 0x27

class ProductionDemo:
    def __init__(self):
        self.production_mode = False
        self.reference_barcode = None
        self.scan_count = 0
        self.pass_count = 0
        self.fail_count = 0
        
        # Initialize hardware
        self.buzzer = Buzzer(BUZZER_PIN)
        self.start_button = Button(START_BTN_PIN, pull_up=True)
        self.capture_button = Button(CAPTURE_BTN_PIN, pull_up=True)
        
        self.lcd = CharLCD('PCF8574', LCD_ADDRESS, cols=16, rows=2)
        self.lcd.clear()
        
        # Set up button handlers
        self.start_button.when_pressed = self.handle_start_button
        self.capture_button.when_pressed = self.handle_capture_button
        
        print("Production Line Demo Initialized!")
        self.display_status("Demo Ready", "Press C to start")
    
    def display_status(self, line1, line2=""):
        """Display status on LCD"""
        self.lcd.clear()
        self.lcd.cursor_pos = (0, 0)
        self.lcd.write_string(line1[:16])
        if line2:
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(line2[:16])
    
    def play_buzzer_tone(self, tone_type):
        """Play different buzzer tones"""
        def buzzer_thread():
            if tone_type == "capture":
                for _ in range(3):
                    self.buzzer.on()
                    time.sleep(0.2)
                    self.buzzer.off()
                    time.sleep(0.1)
            elif tone_type == "start":
                self.buzzer.on()
                time.sleep(0.5)
                self.buzzer.off()
            elif tone_type == "stop":
                for _ in range(2):
                    self.buzzer.on()
                    time.sleep(0.1)
                    self.buzzer.off()
                    time.sleep(0.1)
            elif tone_type == "pass":
                self.buzzer.on()
                time.sleep(0.3)
                self.buzzer.off()
            elif tone_type == "fail":
                for _ in range(2):
                    self.buzzer.on()
                    time.sleep(0.2)
                    self.buzzer.off()
                    time.sleep(0.1)
        
        threading.Thread(target=buzzer_thread, daemon=True).start()
    
    def handle_start_button(self):
        """Handle start/stop button"""
        if not self.reference_barcode:
            self.display_status("No Reference!", "Press C first")
            self.play_buzzer_tone("fail")
            print("Cannot start - no reference set!")
        else:
            self.production_mode = not self.production_mode
            if self.production_mode:
                self.display_status("Production ON", f"Ref: {self.reference_barcode[:8]}...")
                self.play_buzzer_tone("start")
                print("Production mode STARTED")
                self.start_production_simulation()
            else:
                self.display_status("Production OFF", "Press S to start")
                self.play_buzzer_tone("stop")
                print("Production mode STOPPED")
    
    def handle_capture_button(self):
        """Handle capture button"""
        self.reference_barcode = "DEMO123456"
        self.display_status("Reference Set!", f"Code: {self.reference_barcode}")
        self.play_buzzer_tone("capture")
        print(f"Reference captured: {self.reference_barcode}")
    
    def start_production_simulation(self):
        """Simulate production line scanning"""
        def production_thread():
            while self.production_mode:
                self.scan_count += 1
                
                # Simulate scan result (80% pass rate)
                if self.scan_count % 5 != 0:  # 80% pass
                    self.pass_count += 1
                    self.display_status("PASS", f"Scan {self.scan_count}")
                    self.play_buzzer_tone("pass")
                    print(f"Scan {self.scan_count}: PASS")
                else:  # 20% fail
                    self.fail_count += 1
                    self.display_status("FAIL", f"Scan {self.scan_count}")
                    self.play_buzzer_tone("fail")
                    print(f"Scan {self.scan_count}: FAIL")
                
                time.sleep(2)  # 2 second interval between scans
        
        threading.Thread(target=production_thread, daemon=True).start()
    
    def run_demo(self):
        """Run the production demo"""
        print("=" * 50)
        print("PRODUCTION LINE DEMO")
        print("=" * 50)
        print("Hardware Controls:")
        print("  GPIO 27 (C Button) - Capture reference")
        print("  GPIO 22 (S Button) - Start/Stop production")
        print("  GPIO 17 - Buzzer feedback")
        print("  LCD - Status display")
        print("=" * 50)
        print("Demo Workflow:")
        print("1. Press C button to capture reference")
        print("2. Press S button to start production")
        print("3. Watch automatic scanning simulation")
        print("4. Press S again to stop")
        print("=" * 50)
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nDemo stopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.production_mode = False
        self.buzzer.off()
        self.buzzer.close()
        self.start_button.close()
        self.capture_button.close()
        self.lcd.clear()
        self.lcd.close()
        
        print("\nDemo Statistics:")
        print(f"Total Scans: {self.scan_count}")
        print(f"Passed: {self.pass_count}")
        print(f"Failed: {self.fail_count}")
        if self.scan_count > 0:
            pass_rate = (self.pass_count / self.scan_count) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")

if __name__ == "__main__":
    demo = ProductionDemo()
    demo.run_demo()
