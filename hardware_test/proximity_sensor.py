"""
Infrared Proximity Photoelectric Switch Handler
GPIO 24 with internal pullup resistor
"""

import time
from typing import Callable, Optional

# Try to import RPi.GPIO, fall back to simulator on Windows
try:
    import RPi.GPIO as GPIO
    HAS_RPI_GPIO = True
except ImportError:
    HAS_RPI_GPIO = False
    print("Warning: RPi.GPIO not available, using GPIO simulator")

class ProximitySensor:
    def __init__(self, pin=24, pull_up=True, bounce_time=50):
        """
        Initialize proximity sensor
        
        Args:
            pin (int): GPIO pin number (default: 24)
            pull_up (bool): Enable internal pullup resistor (default: True)
            bounce_time (int): Debounce time in milliseconds (default: 50)
        """
        self.pin = pin
        self.pull_up = pull_up
        self.bounce_time = bounce_time
        self.callback = None
        self.is_obstacle_detected = False
        
        # Setup GPIO
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Setup GPIO pin for proximity sensor"""
        if HAS_RPI_GPIO:
            try:
                # Set GPIO mode to BCM
                GPIO.setmode(GPIO.BCM)
                
                # Configure pin with pullup resistor
                if self.pull_up:
                    GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                else:
                    GPIO.setup(self.pin, GPIO.IN)
                
                print(f"Proximity sensor initialized on GPIO {self.pin} with pullup: {self.pull_up}")
                
            except Exception as e:
                print(f"Error setting up GPIO: {e}")
                raise
        else:
            print(f"Proximity sensor simulator initialized on GPIO {self.pin} with pullup: {self.pull_up}")
    
    def read_sensor(self):
        """
        Read current sensor state
        
        Returns:
            bool: True if obstacle detected (light blocked), False if clear
        """
        if HAS_RPI_GPIO:
            try:
                # Read GPIO pin state
                # Note: With pullup, LOW means obstacle detected (sensor pulls down)
                # Without pullup, HIGH might mean obstacle detected (depends on sensor type)
                pin_state = GPIO.input(self.pin)
                
                if self.pull_up:
                    # With pullup: LOW = obstacle detected, HIGH = clear
                    obstacle_detected = not pin_state
                else:
                    # Without pullup: depends on sensor type
                    # Most photoelectric sensors: HIGH = obstacle detected
                    obstacle_detected = bool(pin_state)
                
                self.is_obstacle_detected = obstacle_detected
                return obstacle_detected
                
            except Exception as e:
                print(f"Error reading sensor: {e}")
                return False
        else:
            # Simulator mode - return current state
            return self.is_obstacle_detected
    
    def set_callback(self, callback: Callable[[bool], None]):
        """
        Set callback function for sensor state changes
        
        Args:
            callback: Function to call when sensor state changes
                     Receives boolean: True if obstacle detected, False if clear
        """
        self.callback = callback
        
        # Setup interrupt for both rising and falling edges
        if HAS_RPI_GPIO:
            try:
                if self.pull_up:
                    # With pullup: detect both falling (obstacle) and rising (clear) edges
                    GPIO.add_event_detect(
                        self.pin, 
                        GPIO.BOTH, 
                        callback=self._sensor_callback, 
                        bouncetime=self.bounce_time
                    )
                else:
                    # Without pullup: detect both edges
                    GPIO.add_event_detect(
                        self.pin, 
                        GPIO.BOTH, 
                        callback=self._sensor_callback, 
                        bouncetime=self.bounce_time
                    )
                
                print(f"Callback set for proximity sensor on GPIO {self.pin}")
                
            except Exception as e:
                print(f"Error setting up callback: {e}")
        else:
            print(f"Callback set for proximity sensor simulator on GPIO {self.pin}")
    
    def _sensor_callback(self, channel):
        """Internal callback for GPIO interrupt"""
        if self.callback:
            obstacle_detected = self.read_sensor()
            self.callback(obstacle_detected)
    
    def remove_callback(self):
        """Remove the callback and event detection"""
        if HAS_RPI_GPIO:
            try:
                GPIO.remove_event_detect(self.pin)
                self.callback = None
                print("Callback removed from proximity sensor")
            except Exception as e:
                print(f"Error removing callback: {e}")
        else:
            self.callback = None
            print("Callback removed from proximity sensor simulator")
    
    def get_status_text(self):
        """
        Get human-readable status text
        
        Returns:
            str: Status description
        """
        if self.is_obstacle_detected:
            return "OBSTACLE DETECTED"
        else:
            return "PATH CLEAR"
    
    def simulate_obstacle(self, detected: bool):
        """
        Simulate obstacle detection (for testing without hardware)
        
        Args:
            detected (bool): True to simulate obstacle, False to simulate clear
        """
        if not HAS_RPI_GPIO:
            self.is_obstacle_detected = detected
            if self.callback:
                self.callback(detected)
            print(f"Simulated obstacle detection: {'OBSTACLE' if detected else 'CLEAR'}")
        else:
            print("Cannot simulate on real hardware - use ProximitySensorSimulator instead")
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        try:
            self.remove_callback()
            if HAS_RPI_GPIO:
                GPIO.cleanup(self.pin)
                print("Proximity sensor GPIO cleaned up")
            else:
                print("Proximity sensor simulator cleaned up")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


class ProximitySensorSimulator:
    """
    Simulator for testing without actual hardware
    """
    
    def __init__(self, pin=24):
        self.pin = pin
        self.is_obstacle_detected = False
        self.callback = None
        print(f"Proximity sensor simulator initialized on GPIO {self.pin}")
    
    def read_sensor(self):
        """Simulate sensor reading"""
        return self.is_obstacle_detected
    
    def set_callback(self, callback: Callable[[bool], None]):
        """Set callback for simulator"""
        self.callback = callback
        print(f"Callback set for proximity sensor simulator on GPIO {self.pin}")
    
    def simulate_obstacle(self, detected: bool):
        """Simulate obstacle detection"""
        self.is_obstacle_detected = detected
        if self.callback:
            self.callback(detected)
    
    def remove_callback(self):
        """Remove callback"""
        self.callback = None
        print("Callback removed from proximity sensor simulator")
    
    def get_status_text(self):
        """Get status text"""
        if self.is_obstacle_detected:
            return "OBSTACLE DETECTED"
        else:
            return "PATH CLEAR"
    
    def cleanup(self):
        """Cleanup simulator"""
        self.remove_callback()
        print("Proximity sensor simulator cleaned up")
