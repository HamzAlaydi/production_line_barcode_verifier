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
from buzzer_control import BuzzerControl, BuzzerSimulator
from power_switch import PowerSwitch, PowerSwitchSimulator

class HardwareTestApp:
    def __init__(self, use_simulator=False, buzzer_pin=17, power_switch_pin=22):
        """
        Initialize the hardware test application
        
        Args:
            use_simulator (bool): Use simulator instead of real hardware
            buzzer_pin (int): GPIO pin for buzzer (default: 17)
            power_switch_pin (int): GPIO pin for power switch (default: 22)
        """
        self.use_simulator = use_simulator
        self.buzzer_pin = buzzer_pin
        self.power_switch_pin = power_switch_pin
        self.running = False
        self.system_active = False
        self.lcd = None
        self.sensor = None
        self.buzzer = None
        self.power_switch = None
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
            
            # Initialize buzzer
            print("Initializing buzzer...")
            if self.use_simulator:
                self.buzzer = BuzzerSimulator(pin=self.buzzer_pin)
            else:
                self.buzzer = BuzzerControl(pin=self.buzzer_pin)
            
            # Test buzzer
            print("Testing buzzer...")
            self.buzzer.beep(0.2)
            time.sleep(0.5)
            
            # Initialize power switch
            print("Initializing power switch...")
            if self.use_simulator:
                self.power_switch = PowerSwitchSimulator(pin=self.power_switch_pin)
            else:
                self.power_switch = PowerSwitch(pin=self.power_switch_pin, pull_up=True, bounce_time=50)
            
            # Set callback for power switch
            self.power_switch.set_callback(self._on_power_switch_change)
            
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
        # Only process sensor events when system is active
        if not self.system_active:
            return
            
        current_time = datetime.now()
        
        if obstacle_detected:
            self.obstacle_count += 1
            self.last_obstacle_time = current_time
            print(f"OBSTACLE DETECTED! Count: {self.obstacle_count}")
            
            # Display on LCD
            self.lcd.print_message("OBSTACLE DETECTED", f"Count: {self.obstacle_count}")
            
            # Sound buzzer based on count
            if self.buzzer:
                self.buzzer.obstacle_detected_beep(self.obstacle_count)
        else:
            print("Path clear")
            
            # Display on LCD
            self.lcd.print_message("PATH CLEAR", f"Count: {self.obstacle_count}")
    
    def _on_power_switch_change(self, system_should_be_on):
        """
        Callback function for power switch changes
        
        Args:
            system_should_be_on (bool): True if system should be on, False if off
        """
        self.system_active = system_should_be_on
        
        if self.system_active:
            print("Power switch: SYSTEM TURNED ON")
            if self.lcd:
                self.lcd.print_message("SYSTEM ON", "Monitoring...")
            # Reset obstacle count when turning on
            self.obstacle_count = 0
        else:
            print("Power switch: SYSTEM TURNED OFF")
            if self.lcd:
                self.lcd.print_message("SYSTEM OFF", "Press switch to start")
    
    def display_startup_message(self):
        """Display startup message on LCD"""
        if self.lcd:
            self.lcd.print_message("Hardware Test", "Ready to monitor")
            time.sleep(2)
            self.lcd.print_message("SYSTEM OFF", "Press switch to start")
        
        # Show simulation controls if in simulator mode
        if self.use_simulator or (hasattr(self.sensor, 'bus') and self.sensor.bus is None):
            print("\n" + "="*50)
            print("SIMULATION MODE - Interactive Controls:")
            print("Press 'P' to toggle POWER SWITCH")
            print("Press 'O' to simulate OBSTACLE DETECTED")
            print("Press 'C' to simulate PATH CLEAR")
            print("Press 'Q' to quit")
            print("="*50)
    
    def display_status(self):
        """Display current status on LCD"""
        if not self.lcd or not self.system_active:
            return
        
        # Get current sensor status
        obstacle_detected = self.sensor.read_sensor()
        
        if obstacle_detected:
            status = "OBSTACLE DETECTED"
        else:
            status = "PATH CLEAR"
        
        # Display status and count
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
            last_display_update = 0
            last_sensor_state = None
            
            while self.running:
                # Read sensor state only when system is active
                if self.system_active:
                    obstacle_detected = self.sensor.read_sensor()
                    
                    # Check if sensor state changed
                    if obstacle_detected != last_sensor_state:
                        last_sensor_state = obstacle_detected
                        self._on_sensor_change(obstacle_detected)
                    
                    # Update display every 2 seconds
                    current_time = time.time()
                    if current_time - last_display_update >= 2.0:
                        self.display_status()
                        last_display_update = current_time
                else:
                    # Reset sensor state when system is off
                    last_sensor_state = None
                
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
        
        # Cleanup buzzer
        if self.buzzer:
            self.buzzer.cleanup()
        
        # Cleanup power switch
        if self.power_switch:
            self.power_switch.cleanup()
        
        print("Application stopped successfully")
    
    def get_statistics(self):
        """Get application statistics"""
        return {
            'obstacle_count': self.obstacle_count,
            'last_obstacle_time': self.last_obstacle_time,
            'system_active': self.system_active,
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
                if key == 'p':
                    self.power_switch.simulate_toggle()
                elif key == 'o':
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
    parser.add_argument('--buzzer-pin', type=int, default=17,
                       help='GPIO pin for buzzer (default: 17)')
    parser.add_argument('--power-switch-pin', type=int, default=22,
                       help='GPIO pin for power switch (default: 22)')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Hardware Test Application")
    print("=" * 50)
    print(f"LCD I2C Address: 0x{args.lcd_addr:02X}")
    print(f"Sensor GPIO Pin: {args.sensor_pin}")
    print(f"Buzzer GPIO Pin: {args.buzzer_pin}")
    print(f"Power Switch GPIO Pin: {args.power_switch_pin}")
    print(f"Simulator Mode: {args.simulator}")
    print("=" * 50)
    
    # Create and run application
    app = HardwareTestApp(use_simulator=args.simulator, buzzer_pin=args.buzzer_pin, power_switch_pin=args.power_switch_pin)
    
    try:
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
