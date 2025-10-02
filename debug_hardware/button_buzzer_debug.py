#!/usr/bin/env python3
"""
Button and Buzzer Debugging Tool
Separate project for testing GPIO buttons and buzzer hardware
"""

import time
import threading
import sys

# GPIO imports with fallback
try:
    import RPi.GPIO as GPIO
    GPIO_LIBRARY = "RPi.GPIO"
    print("✅ Using RPi.GPIO library")
except ImportError:
    try:
        import RPi.lgpio as GPIO
        GPIO_LIBRARY = "RPi.lgpio"
        print("✅ Using RPi.lgpio library")
    except ImportError:
        GPIO = None
        GPIO_LIBRARY = None
        print("❌ No GPIO library available - running in simulation mode")

class ButtonBuzzerDebugger:
    def __init__(self):
        # GPIO Pin Configuration (matching main system)
        self.BUZZER_PIN = 17      # Buzzer on GPIO 17
        self.START_BTN_PIN = 22   # Start/Stop button on GPIO 22
        self.CAPTURE_BTN_PIN = 27 # Capture reference button on GPIO 27
        
        # Button state tracking
        self.last_start_btn_state = 1  # HIGH (not pressed)
        self.last_capture_btn_state = 1  # HIGH (not pressed)
        
        # Statistics
        self.start_presses = 0
        self.capture_presses = 0
        self.buzzer_tests = 0
        
        # Initialize GPIO
        self.setup_gpio()
        
        print("🔧 Button & Buzzer Debugger Initialized!")
        print("=" * 60)
        print("HARDWARE CONFIGURATION:")
        print(f"  Buzzer: GPIO {self.BUZZER_PIN}")
        print(f"  Start Button: GPIO {self.START_BTN_PIN}")
        print(f"  Capture Button: GPIO {self.CAPTURE_BTN_PIN}")
        print("=" * 60)
    
    def setup_gpio(self):
        """Initialize GPIO pins for buzzer and buttons"""
        if GPIO is None:
            print("⚠️  No GPIO library - running in simulation mode")
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
            
            print("✅ GPIO pins configured successfully")
            print("  🔌 Buzzer: GPIO 17 (OUTPUT)")
            print("  🔘 Start Button: GPIO 22 (INPUT with PUD_UP)")
            print("  🔘 Capture Button: GPIO 27 (INPUT with PUD_UP)")
            
        except Exception as e:
            print(f"❌ GPIO setup failed: {e}")
            print("Running in simulation mode")
    
    def buzzer_beep(self, duration=0.3, pattern="single"):
        """Generate buzzer beep with different patterns"""
        if GPIO is None:
            print(f"🔊 [SIM] Buzzer beep: {pattern} ({duration}s)")
            return
            
        try:
            if pattern == "single":
                self._buzzer_on_off(duration)
            elif pattern == "double":
                self._buzzer_on_off(0.2)
                time.sleep(0.1)
                self._buzzer_on_off(0.2)
            elif pattern == "triple":
                for _ in range(3):
                    self._buzzer_on_off(0.2)
                    time.sleep(0.1)
            elif pattern == "error":
                for _ in range(3):
                    self._buzzer_on_off(0.1)
                    time.sleep(0.1)
            elif pattern == "long":
                self._buzzer_on_off(duration)
            
            self.buzzer_tests += 1
            print(f"🔊 Buzzer test #{self.buzzer_tests}: {pattern} pattern")
            
        except Exception as e:
            print(f"❌ Buzzer error: {e}")
    
    def _buzzer_on_off(self, duration):
        """Simple buzzer ON/OFF control"""
        if GPIO_LIBRARY == "RPi.GPIO":
            GPIO.output(self.BUZZER_PIN, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.BUZZER_PIN, GPIO.LOW)
        elif GPIO_LIBRARY == "RPi.lgpio":
            GPIO.gpio_write(self.gpio_handle, self.BUZZER_PIN, 1)
            time.sleep(duration)
            GPIO.gpio_write(self.gpio_handle, self.BUZZER_PIN, 0)
    
    def check_buttons(self):
        """Check button states and handle presses"""
        if GPIO is None:
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
            print(f"❌ Button check error: {e}")
    
    def handle_start_button(self):
        """Handle start/stop button press"""
        self.start_presses += 1
        print(f"🔘 START BUTTON PRESSED! (#{self.start_presses})")
        self.buzzer_beep(0.3, "single")
    
    def handle_capture_button(self):
        """Handle capture reference button press"""
        self.capture_presses += 1
        print(f"🔘 CAPTURE BUTTON PRESSED! (#{self.capture_presses})")
        self.buzzer_beep(0.2, "triple")
    
    def test_buzzer_patterns(self):
        """Test all buzzer patterns"""
        print("\n🎵 TESTING ALL BUZZER PATTERNS")
        print("=" * 40)
        
        patterns = [
            ("Single beep", "single", 0.3),
            ("Double beep", "double", 0.0),
            ("Triple beep", "triple", 0.0),
            ("Error pattern", "error", 0.0),
            ("Long beep", "long", 0.8),
        ]
        
        for name, pattern, duration in patterns:
            print(f"Testing: {name}")
            self.buzzer_beep(duration, pattern)
            time.sleep(0.5)
        
        print("✅ All buzzer patterns tested!")
    
    def test_buttons_continuous(self):
        """Test buttons continuously"""
        print("\n🔘 TESTING BUTTONS CONTINUOUSLY")
        print("=" * 40)
        print("Press the buttons to test them!")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                self.check_buttons()
                time.sleep(0.01)  # 10ms polling
        except KeyboardInterrupt:
            print("\n⏹️  Button testing stopped by user")
    
    def show_button_states(self):
        """Show current button states"""
        if GPIO is None:
            print("🔘 [SIM] Start Button: HIGH (not pressed)")
            print("🔘 [SIM] Capture Button: HIGH (not pressed)")
            return
            
        try:
            if GPIO_LIBRARY == "RPi.GPIO":
                start_state = GPIO.input(self.START_BTN_PIN)
                capture_state = GPIO.input(self.CAPTURE_BTN_PIN)
            elif GPIO_LIBRARY == "RPi.lgpio":
                start_state = GPIO.gpio_read(self.gpio_handle, self.START_BTN_PIN)
                capture_state = GPIO.gpio_read(self.gpio_handle, self.CAPTURE_BTN_PIN)
            
            start_status = "PRESSED" if start_state == 0 else "NOT PRESSED"
            capture_status = "PRESSED" if capture_state == 0 else "NOT PRESSED"
            
            print(f"🔘 Start Button (GPIO 22): {start_status} (raw: {start_state})")
            print(f"🔘 Capture Button (GPIO 27): {capture_status} (raw: {capture_state})")
            
        except Exception as e:
            print(f"❌ Error reading button states: {e}")
    
    def print_statistics(self):
        """Print test statistics"""
        print("\n" + "=" * 60)
        print("📊 TEST STATISTICS")
        print("=" * 60)
        print(f"Start Button Presses:  {self.start_presses}")
        print(f"Capture Button Presses: {self.capture_presses}")
        print(f"Buzzer Tests:          {self.buzzer_tests}")
        print("=" * 60)
    
    def cleanup(self):
        """Cleanup GPIO"""
        try:
            if GPIO is not None:
                if GPIO_LIBRARY == "RPi.GPIO":
                    GPIO.cleanup()
                elif GPIO_LIBRARY == "RPi.lgpio":
                    GPIO.gpiochip_close(self.gpio_handle)
            print("✅ GPIO cleanup completed")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
    
    def interactive_menu(self):
        """Interactive testing menu"""
        while True:
            print("\n" + "=" * 60)
            print("🔧 BUTTON & BUZZER DEBUG MENU")
            print("=" * 60)
            print("1. Test buzzer patterns")
            print("2. Test buttons continuously")
            print("3. Show button states")
            print("4. Single buzzer beep")
            print("5. Print statistics")
            print("6. Exit")
            print("=" * 60)
            
            try:
                choice = input("Enter your choice (1-6): ").strip()
                
                if choice == "1":
                    self.test_buzzer_patterns()
                elif choice == "2":
                    self.test_buttons_continuous()
                elif choice == "3":
                    self.show_button_states()
                elif choice == "4":
                    self.buzzer_beep(0.3, "single")
                elif choice == "5":
                    self.print_statistics()
                elif choice == "6":
                    print("👋 Exiting debugger...")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-6.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting debugger...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 Starting Button & Buzzer Debugger...")
    
    debugger = ButtonBuzzerDebugger()
    
    try:
        # Check if command line arguments provided
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "buzzer":
                debugger.test_buzzer_patterns()
            elif command == "buttons":
                debugger.test_buttons_continuous()
            elif command == "states":
                debugger.show_button_states()
            elif command == "beep":
                debugger.buzzer_beep(0.3, "single")
            else:
                print(f"❌ Unknown command: {command}")
                print("Available commands: buzzer, buttons, states, beep")
        else:
            # Interactive mode
            debugger.interactive_menu()
            
    except KeyboardInterrupt:
        print("\n⏹️  Debugger interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        debugger.print_statistics()
        debugger.cleanup()

if __name__ == "__main__":
    main()
