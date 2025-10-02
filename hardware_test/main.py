#!/usr/bin/env python3
"""
Hardware Test Application
I2C LCD Display + Infrared Proximity Sensor

Hardware Setup:
- I2C LCD on GPIO SCL/SDA (I2C bus 1, address 0x27)
- Infrared Proximity Sensor on GPIO 24 with pullup resistor

The application monitors the proximity sensor and displays status on the LCD.
When something cuts the light beam, it shows "OBSTACLE DETECTED" on the LCD.
"""

import time
import signal
import sys
from datetime import datetime
from i2c_lcd import I2CLCD
from proximity_sensor import ProximitySensor, ProximitySensorSimulator

class HardwareTestApp:
    def __init__(self, use_simulator=False):
        """
        Initialize the hardware test application
        
        Args:
            use_simulator (bool): Use simulator instead of real hardware
        """
        self.use_simulator = use_simulator
        self.running = False
        self.lcd = None
        self.sensor = None
        self.obstacle_count = 0
        self.last_obstacle_time = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.stop()
    
    def initialize_hardware(self):
        """Initialize LCD and proximity sensor"""
        try:
            # Initialize LCD
            print("Initializing I2C LCD...")
            self.lcd = I2CLCD(i2c_bus=1, i2c_addr=0x27, rows=2, cols=16)
            self.lcd.backlight_on()
            self.lcd.print_message("Hardware Test", "Initializing...")
            time.sleep(1)
            
            # Initialize proximity sensor
            print("Initializing proximity sensor...")
            if self.use_simulator:
                self.sensor = ProximitySensorSimulator(pin=24)
            else:
                self.sensor = ProximitySensor(pin=24, pull_up=True, bounce_time=50)
            
            # Set callback for sensor state changes
            self.sensor.set_callback(self._on_sensor_change)
            
            print("Hardware initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Error initializing hardware: {e}")
            return False
    
    def _on_sensor_change(self, obstacle_detected):
        """
        Callback function for sensor state changes
        
        Args:
            obstacle_detected (bool): True if obstacle detected, False if clear
        """
        current_time = datetime.now()
        
        if obstacle_detected:
            self.obstacle_count += 1
            self.last_obstacle_time = current_time
            print(f"OBSTACLE DETECTED! Count: {self.obstacle_count}")
            
            # Display on LCD
            self.lcd.print_message("OBSTACLE DETECTED", f"Count: {self.obstacle_count}")
        else:
            print("Path clear")
            
            # Display on LCD
            self.lcd.print_message("PATH CLEAR", f"Count: {self.obstacle_count}")
    
    def display_startup_message(self):
        """Display startup message on LCD"""
        if self.lcd:
            self.lcd.print_message("Hardware Test", "Ready to monitor")
            time.sleep(2)
            self.lcd.print_message("Monitoring...", "Waiting for input")
        
        # Show simulation controls if in simulator mode
        if self.use_simulator or (hasattr(self.sensor, 'bus') and self.sensor.bus is None):
            print("\n" + "="*50)
            print("SIMULATION MODE - Interactive Controls:")
            print("Press 'O' to simulate OBSTACLE DETECTED")
            print("Press 'C' to simulate PATH CLEAR")
            print("Press 'Q' to quit")
            print("="*50)
    
    def display_status(self):
        """Display current status on LCD"""
        if not self.lcd:
            return
        
        current_time = datetime.now().strftime("%H:%M:%S")
        status = self.sensor.get_status_text()
        
        if self.last_obstacle_time:
            time_since = current_time
            self.lcd.print_message(f"{status}", f"Count: {self.obstacle_count}")
        else:
            self.lcd.print_message(f"{status}", f"Count: {self.obstacle_count}")
    
    def run(self):
        """Main application loop"""
        print("Starting Hardware Test Application...")
        print("Press Ctrl+C to stop")
        
        if not self.initialize_hardware():
            print("Failed to initialize hardware. Exiting.")
            return
        
        self.display_startup_message()
        self.running = True
        
        try:
            while self.running:
                # Read sensor state
                obstacle_detected = self.sensor.read_sensor()
                
                # Update display every 5 seconds
                if int(time.time()) % 5 == 0:
                    self.display_status()
                
                # Check for keyboard input for simulation (Windows/development mode)
                if self.use_simulator or (hasattr(self.lcd, 'bus') and self.lcd.bus is None):
                    self._check_simulation_input()
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application and cleanup resources"""
        print("Stopping application...")
        self.running = False
        
        # Display shutdown message
        if self.lcd:
            self.lcd.print_message("Shutting down...", "Goodbye!")
            time.sleep(1)
            self.lcd.backlight_off()
            self.lcd.close()
        
        # Cleanup sensor
        if self.sensor:
            self.sensor.cleanup()
        
        print("Application stopped successfully")
    
    def get_statistics(self):
        """Get application statistics"""
        return {
            'obstacle_count': self.obstacle_count,
            'last_obstacle_time': self.last_obstacle_time,
            'current_status': self.sensor.get_status_text() if self.sensor else "Unknown"
        }
    
    def _check_simulation_input(self):
        """Check for keyboard input to simulate sensor events"""
        import sys
        import msvcrt  # Windows-specific
        
        try:
            # Check if a key is pressed (Windows)
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                if key == 'o':
                    self.sensor.simulate_obstacle(True)
                elif key == 'c':
                    self.sensor.simulate_obstacle(False)
                elif key == 'q':
                    self.stop()
        except:
            # Fallback for non-Windows systems
            pass


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hardware Test Application')
    parser.add_argument('--simulator', action='store_true', 
                       help='Use simulator instead of real hardware')
    parser.add_argument('--lcd-addr', type=int, default=0x27,
                       help='I2C address for LCD (default: 0x27)')
    parser.add_argument('--sensor-pin', type=int, default=24,
                       help='GPIO pin for proximity sensor (default: 24)')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Hardware Test Application")
    print("=" * 50)
    print(f"LCD I2C Address: 0x{args.lcd_addr:02X}")
    print(f"Sensor GPIO Pin: {args.sensor_pin}")
    print(f"Simulator Mode: {args.simulator}")
    print("=" * 50)
    
    # Create and run application
    app = HardwareTestApp(use_simulator=args.simulator)
    
    try:
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
