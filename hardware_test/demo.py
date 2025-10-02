#!/usr/bin/env python3
"""
Hardware Test Demo - Windows Compatible
Demonstrates the hardware test application functionality without requiring actual hardware
"""

import time
import sys
from datetime import datetime

class HardwareTestDemo:
    def __init__(self):
        self.obstacle_count = 0
        self.last_obstacle_time = None
        self.is_obstacle_detected = False
        self.running = False
        
    def simulate_obstacle_detection(self, detected):
        """Simulate obstacle detection"""
        current_time = datetime.now()
        
        if detected:
            self.obstacle_count += 1
            self.last_obstacle_time = current_time
            self.is_obstacle_detected = True
            print(f"[RED] OBSTACLE DETECTED! Count: {self.obstacle_count}")
            self.display_lcd("OBSTACLE DETECTED", f"Count: {self.obstacle_count}")
        else:
            self.is_obstacle_detected = False
            print("[GREEN] Path clear")
            self.display_lcd("PATH CLEAR", f"Count: {self.obstacle_count}")
    
    def display_lcd(self, line1, line2=""):
        """Simulate LCD display"""
        print("=" * 20)
        print("LCD Display:")
        print(f"Line 1: {line1}")
        if line2:
            print(f"Line 2: {line2}")
        print("=" * 20)
    
    def show_status(self):
        """Show current status"""
        status = "OBSTACLE DETECTED" if self.is_obstacle_detected else "PATH CLEAR"
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"\nStatus at {current_time}:")
        print(f"   Sensor State: {status}")
        print(f"   Obstacle Count: {self.obstacle_count}")
        if self.last_obstacle_time:
            print(f"   Last Detection: {self.last_obstacle_time.strftime('%H:%M:%S')}")
    
    def run_demo(self):
        """Run the interactive demo"""
        print("=" * 60)
        print("HARDWARE TEST APPLICATION DEMO")
        print("=" * 60)
        print("This demo simulates:")
        print("- I2C LCD Display (16x2) on GPIO SCL/SDA")
        print("- Infrared Proximity Sensor on GPIO 24 with pullup")
        print("- Real-time monitoring and display")
        print("=" * 60)
        
        # Initial display
        self.display_lcd("Hardware Test", "Ready to monitor")
        time.sleep(2)
        self.display_lcd("Monitoring...", "Waiting for input")
        
        print("\nInteractive Controls:")
        print("- Press 'O' to simulate OBSTACLE DETECTED")
        print("- Press 'C' to simulate PATH CLEAR")
        print("- Press 'S' to show current status")
        print("- Press 'Q' to quit")
        print("- Press 'H' to show this help")
        print("\nStarting demo... Press any key to begin!")
        
        self.running = True
        
        try:
            while self.running:
                # Show periodic status updates
                if int(time.time()) % 10 == 0:
                    self.show_status()
                
                # Check for keyboard input (Windows compatible)
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        if key == 'o':
                            self.simulate_obstacle_detection(True)
                        elif key == 'c':
                            self.simulate_obstacle_detection(False)
                        elif key == 's':
                            self.show_status()
                        elif key == 'q':
                            self.stop_demo()
                        elif key == 'h':
                            self.show_help()
                        else:
                            print("Unknown command. Press 'H' for help.")
                except ImportError:
                    # Fallback for non-Windows systems
                    pass
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
            self.stop_demo()
        except Exception as e:
            print(f"\nError in demo: {e}")
            self.stop_demo()
    
    def show_help(self):
        """Show help information"""
        print("\nHELP - Hardware Test Demo")
        print("=" * 40)
        print("Commands:")
        print("  O - Simulate obstacle detection")
        print("  C - Simulate path clear")
        print("  S - Show current status")
        print("  H - Show this help")
        print("  Q - Quit demo")
        print("=" * 40)
    
    def stop_demo(self):
        """Stop the demo"""
        print("\nStopping demo...")
        self.display_lcd("Shutting down...", "Goodbye!")
        time.sleep(1)
        self.display_lcd("Demo Complete", f"Total: {self.obstacle_count}")
        
        print(f"\nFinal Statistics:")
        print(f"   Total Obstacles Detected: {self.obstacle_count}")
        print(f"   Final Status: {'OBSTACLE DETECTED' if self.is_obstacle_detected else 'PATH CLEAR'}")
        
        self.running = False
        print("Demo completed successfully!")


def main():
    """Main function"""
    print("Starting Hardware Test Demo...")
    
    # Check if we're on Windows
    if sys.platform == "win32":
        print("Running on Windows - using demo mode")
    else:
        print("Running on Linux - could use real hardware")
    
    demo = HardwareTestDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
