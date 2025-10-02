"""
Power Switch Control for GPIO 22
Toggle switch to turn system on/off
"""

import time
from typing import Callable, Optional

# Try to import RPi.GPIO, fall back to simulator on Windows
try:
    import RPi.GPIO as GPIO
    HAS_RPI_GPIO = True
except ImportError:
    HAS_RPI_GPIO = False
    print("Warning: RPi.GPIO not available, using power switch simulator")

class PowerSwitch:
    def __init__(self, pin=22, pull_up=True, bounce_time=50):
        """
        Initialize power switch
        
        Args:
            pin (int): GPIO pin number for power switch (default: 22)
            pull_up (bool): Enable internal pullup resistor (default: True)
            bounce_time (int): Debounce time in milliseconds (default: 50)
        """
        self.pin = pin
        self.pull_up = pull_up
        self.bounce_time = bounce_time
        self.callback = None
        self.is_system_on = False
        self.last_press_time = 0
        self.debounce_delay = 0.2  # 200ms debounce
        
        # Setup GPIO
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Setup GPIO pin for power switch"""
        if HAS_RPI_GPIO:
            try:
                # Set GPIO mode to BCM
                GPIO.setmode(GPIO.BCM)
                
                # Configure pin with pullup resistor
                if self.pull_up:
                    GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                else:
                    GPIO.setup(self.pin, GPIO.IN)
                
                print(f"Power switch initialized on GPIO {self.pin} with pullup: {self.pull_up}")
                
            except Exception as e:
                print(f"Error setting up power switch GPIO: {e}")
                raise
        else:
            print(f"Power switch simulator initialized on GPIO {self.pin} with pullup: {self.pull_up}")
    
    def read_switch(self):
        """
        Read current switch state
        
        Returns:
            bool: True if switch is pressed (system should be on), False if released
        """
        if HAS_RPI_GPIO:
            try:
                # Read GPIO pin state
                # With pullup: LOW = pressed, HIGH = released
                pin_state = GPIO.input(self.pin)
                
                if self.pull_up:
                    # With pullup: LOW = pressed, HIGH = released
                    switch_pressed = not pin_state
                else:
                    # Without pullup: depends on switch wiring
                    switch_pressed = bool(pin_state)
                
                return switch_pressed
                
            except Exception as e:
                print(f"Error reading power switch: {e}")
                return False
        else:
            # Simulator mode - return current state
            return self.is_system_on
    
    def set_callback(self, callback: Callable[[bool], None]):
        """
        Set callback function for switch state changes
        
        Args:
            callback: Function to call when switch state changes
                     Receives boolean: True if system should be on, False if off
        """
        self.callback = callback
        
        # Setup interrupt for both rising and falling edges
        if HAS_RPI_GPIO:
            try:
                if self.pull_up:
                    # With pullup: detect both falling (pressed) and rising (released) edges
                    GPIO.add_event_detect(
                        self.pin, 
                        GPIO.BOTH, 
                        callback=self._switch_callback, 
                        bouncetime=self.bounce_time
                    )
                else:
                    # Without pullup: detect both edges
                    GPIO.add_event_detect(
                        self.pin, 
                        GPIO.BOTH, 
                        callback=self._switch_callback, 
                        bouncetime=self.bounce_time
                    )
                
                print(f"Callback set for power switch on GPIO {self.pin}")
                
            except Exception as e:
                print(f"Error setting up power switch callback: {e}")
        else:
            print(f"Callback set for power switch simulator on GPIO {self.pin}")
    
    def _switch_callback(self, channel):
        """Internal callback for GPIO interrupt"""
        if self.callback:
            current_time = time.time()
            
            # Debounce check
            if current_time - self.last_press_time < self.debounce_delay:
                return
            
            self.last_press_time = current_time
            
            # Read switch state and toggle system
            switch_pressed = self.read_switch()
            if switch_pressed:
                self.is_system_on = not self.is_system_on
                self.callback(self.is_system_on)
    
    def remove_callback(self):
        """Remove the callback and event detection"""
        if HAS_RPI_GPIO:
            try:
                GPIO.remove_event_detect(self.pin)
                self.callback = None
                print("Callback removed from power switch")
            except Exception as e:
                print(f"Error removing power switch callback: {e}")
        else:
            self.callback = None
            print("Callback removed from power switch simulator")
    
    def get_status_text(self):
        """
        Get human-readable status text
        
        Returns:
            str: Status description
        """
        if self.is_system_on:
            return "SYSTEM ON"
        else:
            return "SYSTEM OFF"
    
    def simulate_toggle(self):
        """
        Simulate switch toggle (for testing without hardware)
        """
        if not HAS_RPI_GPIO:
            self.is_system_on = not self.is_system_on
            if self.callback:
                self.callback(self.is_system_on)
            print(f"Simulated power switch toggle: {'ON' if self.is_system_on else 'OFF'}")
        else:
            print("Cannot simulate on real hardware - use PowerSwitchSimulator instead")
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        try:
            self.remove_callback()
            if HAS_RPI_GPIO:
                GPIO.cleanup(self.pin)
                print("Power switch GPIO cleaned up")
            else:
                print("Power switch simulator cleaned up")
        except Exception as e:
            print(f"Error during power switch cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


class PowerSwitchSimulator:
    """
    Simulator for testing without actual power switch hardware
    """
    
    def __init__(self, pin=22):
        self.pin = pin
        self.is_system_on = False
        self.callback = None
        print(f"Power switch simulator initialized on GPIO {self.pin}")
    
    def read_switch(self):
        """Simulate switch reading"""
        return self.is_system_on
    
    def set_callback(self, callback: Callable[[bool], None]):
        """Set callback for simulator"""
        self.callback = callback
        print(f"Callback set for power switch simulator on GPIO {self.pin}")
    
    def simulate_toggle(self):
        """Simulate switch toggle"""
        self.is_system_on = not self.is_system_on
        if self.callback:
            self.callback(self.is_system_on)
        print(f"Simulated power switch toggle: {'ON' if self.is_system_on else 'OFF'}")
    
    def remove_callback(self):
        """Remove callback"""
        self.callback = None
        print("Callback removed from power switch simulator")
    
    def get_status_text(self):
        """Get status text"""
        if self.is_system_on:
            return "SYSTEM ON"
        else:
            return "SYSTEM OFF"
    
    def cleanup(self):
        """Cleanup simulator"""
        self.remove_callback()
        print("Power switch simulator cleaned up")
