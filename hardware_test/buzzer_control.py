"""
Buzzer Control for GPIO 17
Simple buzzer control with beep patterns
"""

import time
from typing import Optional

# Try to import RPi.GPIO, fall back to simulator on Windows
try:
    import RPi.GPIO as GPIO
    HAS_RPI_GPIO = True
except ImportError:
    HAS_RPI_GPIO = False
    print("Warning: RPi.GPIO not available, using buzzer simulator")

class BuzzerControl:
    def __init__(self, pin=17):
        """
        Initialize buzzer control
        
        Args:
            pin (int): GPIO pin number for buzzer (default: 17)
        """
        self.pin = pin
        self.is_active = False
        
        # Setup GPIO
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Setup GPIO pin for buzzer"""
        if HAS_RPI_GPIO:
            try:
                # Set GPIO mode to BCM (only if not already set)
                try:
                    GPIO.setmode(GPIO.BCM)
                except:
                    pass  # Already set
                
                # Configure pin as output
                GPIO.setup(self.pin, GPIO.OUT)
                
                # Start with buzzer off
                GPIO.output(self.pin, GPIO.LOW)
                self.is_active = False
                
                print(f"Buzzer initialized on GPIO {self.pin}")
                
            except Exception as e:
                print(f"Error setting up buzzer GPIO: {e}")
                raise
        else:
            print(f"Buzzer simulator initialized on GPIO {self.pin}")
    
    def beep(self, duration=0.1):
        """
        Make a single beep
        
        Args:
            duration (float): Duration of beep in seconds (default: 0.1)
        """
        if HAS_RPI_GPIO:
            try:
                # Turn buzzer on
                GPIO.output(self.pin, GPIO.HIGH)
                self.is_active = True
                time.sleep(duration)
                # Turn buzzer off
                GPIO.output(self.pin, GPIO.LOW)
                self.is_active = False
                print(f"Buzzer beeped for {duration}s")
            except Exception as e:
                print(f"Error controlling buzzer: {e}")
        else:
            print(f"Buzzer simulator: BEEP for {duration}s")
    
    def beep_pattern(self, pattern="single", count=1):
        """
        Make a beep pattern
        
        Args:
            pattern (str): Pattern type - "single", "double", "triple", "long"
            count (int): Number of times to repeat pattern
        """
        for _ in range(count):
            if pattern == "single":
                self.beep(0.1)
            elif pattern == "double":
                self.beep(0.1)
                time.sleep(0.1)
                self.beep(0.1)
            elif pattern == "triple":
                self.beep(0.1)
                time.sleep(0.1)
                self.beep(0.1)
                time.sleep(0.1)
                self.beep(0.1)
            elif pattern == "long":
                self.beep(0.5)
            
            # Pause between pattern repetitions
            if count > 1:
                time.sleep(0.2)
    
    def obstacle_detected_beep(self, obstacle_count):
        """
        Make appropriate beep based on obstacle count
        
        Args:
            obstacle_count (int): Current obstacle count
        """
        if obstacle_count == 1:
            # First detection - single beep
            self.beep_pattern("single", 1)
        elif obstacle_count <= 3:
            # Few detections - double beep
            self.beep_pattern("double", 1)
        elif obstacle_count <= 10:
            # Multiple detections - triple beep
            self.beep_pattern("triple", 1)
        else:
            # Many detections - long beep
            self.beep_pattern("long", 1)
    
    def test_sequence(self):
        """Test all buzzer patterns"""
        print("Testing buzzer patterns...")
        
        patterns = [
            ("single", 1),
            ("double", 1),
            ("triple", 1),
            ("long", 1)
        ]
        
        for pattern, count in patterns:
            print(f"Testing {pattern} pattern...")
            self.beep_pattern(pattern, count)
            time.sleep(0.5)
        
        print("Buzzer test complete!")
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        try:
            if HAS_RPI_GPIO:
                try:
                    GPIO.output(self.pin, GPIO.LOW)
                except:
                    pass  # Pin might not be set up
                try:
                    GPIO.cleanup(self.pin)
                except:
                    pass  # Pin might not be set up
                print("Buzzer GPIO cleaned up")
            else:
                print("Buzzer simulator cleaned up")
        except Exception as e:
            print(f"Error during buzzer cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


class BuzzerSimulator:
    """
    Simulator for testing without actual buzzer hardware
    """
    
    def __init__(self, pin=17):
        self.pin = pin
        print(f"Buzzer simulator initialized on GPIO {self.pin}")
    
    def beep(self, duration=0.1):
        """Simulate beep"""
        print(f"Buzzer simulator: BEEP for {duration}s")
        time.sleep(duration)
    
    def beep_pattern(self, pattern="single", count=1):
        """Simulate beep pattern"""
        print(f"Buzzer simulator: {pattern} pattern x{count}")
        for _ in range(count):
            if pattern == "single":
                self.beep(0.1)
            elif pattern == "double":
                self.beep(0.1)
                time.sleep(0.1)
                self.beep(0.1)
            elif pattern == "triple":
                self.beep(0.1)
                time.sleep(0.1)
                self.beep(0.1)
                time.sleep(0.1)
                self.beep(0.1)
            elif pattern == "long":
                self.beep(0.5)
            
            if count > 1:
                time.sleep(0.2)
    
    def obstacle_detected_beep(self, obstacle_count):
        """Simulate obstacle detection beep"""
        if obstacle_count == 1:
            self.beep_pattern("single", 1)
        elif obstacle_count <= 3:
            self.beep_pattern("double", 1)
        elif obstacle_count <= 10:
            self.beep_pattern("triple", 1)
        else:
            self.beep_pattern("long", 1)
    
    def test_sequence(self):
        """Test all buzzer patterns"""
        print("Testing buzzer simulator patterns...")
        patterns = [("single", 1), ("double", 1), ("triple", 1), ("long", 1)]
        for pattern, count in patterns:
            print(f"Testing {pattern} pattern...")
            self.beep_pattern(pattern, count)
            time.sleep(0.5)
        print("Buzzer simulator test complete!")
    
    def cleanup(self):
        """Cleanup simulator"""
        print("Buzzer simulator cleaned up")
