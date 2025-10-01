#!/usr/bin/env python3
"""
Production Line Barcode Verification System
Designed for Raspberry Pi, adapted for laptop testing.

Keyboard Controls (simulating buttons):
- 'c' = Capture reference barcode (Capture Button)
- 's' = Start/Stop production verification (Start Button)
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
import winsound  # For Windows beep sounds


class ProductionLineVerifier:
    """Barcode verification system for production line quality control."""
    
    def __init__(self):
        self.reference_barcode = None
        self.reference_type = None
        self.production_mode = False
        self.log_file = "production_log.csv"
        
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
        
        # Initialize log file
        self._initialize_log_file()
        
        print("Production Line Barcode Verification System")
        print("=" * 60)
        print("System initialized successfully!")
    
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
    
    def play_sound(self, sound_type):
        """Play different sounds for different events (Windows only)."""
        try:
            if sound_type == 'success':
                # Short high beep for success
                winsound.Beep(1000, 100)
            elif sound_type == 'mismatch':
                # Two medium beeps for mismatch
                winsound.Beep(800, 200)
                time.sleep(0.1)
                winsound.Beep(800, 200)
            elif sound_type == 'no_barcode':
                # Long low beep for no barcode
                winsound.Beep(400, 500)
            elif sound_type == 'reference_captured':
                # Three ascending beeps for reference capture
                winsound.Beep(600, 100)
                time.sleep(0.05)
                winsound.Beep(800, 100)
                time.sleep(0.05)
                winsound.Beep(1000, 100)
        except Exception as e:
            # Silently fail if sound doesn't work (non-Windows systems)
            pass
    
    def detect_barcode(self, frame):
        """Detect and decode barcodes from frame."""
        # Convert to grayscale for better detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Enhance image for better detection
        enhanced = cv2.equalizeHist(gray)
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Detect barcodes
        barcodes = pyzbar.decode(enhanced)
        
        return barcodes
    
    def capture_reference(self, frame):
        """Capture and store reference barcode from current frame."""
        barcodes = self.detect_barcode(frame)
        
        if not barcodes:
            print("[ERROR] No barcode detected! Please position product correctly and try again.")
            self.play_sound('no_barcode')
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
        print("You can now start production verification (press 's')")
        print()
        
        self.log_result('REFERENCE_SET', self.reference_barcode, self.reference_type)
        self.play_sound('reference_captured')
        
        return True
    
    def verify_product(self, frame):
        """Verify product barcode against reference."""
        if not self.reference_barcode:
            print("[WARNING] No reference barcode set! Press 'c' to capture reference first.")
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
            self.log_result('NO_BARCODE', '', '')
            self.play_sound('no_barcode')
            return 'NO_BARCODE'
        
        # Check first barcode
        barcode = barcodes[0]
        detected_barcode = barcode.data.decode('utf-8')
        detected_type = barcode.type
        
        if detected_barcode == self.reference_barcode:
            # Match - product is correct
            self.stats['passed'] += 1
            print(f"[PASS] (Scan #{self.stats['total_scans']}): {detected_barcode}")
            self.log_result('PASS', detected_barcode, detected_type)
            self.play_sound('success')
            return 'PASS'
        else:
            # Mismatch - wrong product
            self.stats['mismatched'] += 1
            print(f"\n[ALERT] BARCODE MISMATCH (Scan #{self.stats['total_scans']})")
            print(f"   Expected: {self.reference_barcode}")
            print(f"   Found:    {detected_barcode}")
            self.log_result('MISMATCH', detected_barcode, detected_type)
            self.play_sound('mismatch')
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
        cv2.rectangle(overlay, (0, 0), (width, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display, 0.3, 0, display)
        
        # Title
        cv2.putText(display, "PRODUCTION LINE BARCODE VERIFIER", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Reference barcode status
        if self.reference_barcode:
            ref_text = f"Reference: {self.reference_barcode} ({self.reference_type})"
            cv2.putText(display, ref_text, (20, 75), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(display, "Reference: NOT SET - Press 'C' to capture", 
                       (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Production mode status
        if self.production_mode:
            mode_text = "Mode: PRODUCTION ACTIVE"
            mode_color = (0, 255, 0)
        else:
            mode_text = "Mode: STANDBY - Press 'S' to start"
            mode_color = (255, 255, 0)
        cv2.putText(display, mode_text, (20, 105), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
        
        # Statistics
        stats_text = f"Scans: {self.stats['total_scans']} | Pass: {self.stats['passed']} | Mismatch: {self.stats['mismatched']} | No Barcode: {self.stats['no_barcode']}"
        cv2.putText(display, stats_text, (20, 135), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Performance
        if self.stats['total_scans'] > 0:
            pass_rate = (self.stats['passed'] / self.stats['total_scans']) * 100
            perf_text = f"Pass Rate: {pass_rate:.1f}%"
            cv2.putText(display, perf_text, (20, 165), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Controls
        controls_y = height - 30
        cv2.putText(display, "Controls: C=Capture Ref | S=Start/Stop | R=Reset | L=Logs | Q=Quit", 
                   (20, controls_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
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
                # Show header and last 20 entries
                if len(lines) > 0:
                    print(lines[0].strip())  # Header
                    print("-" * 60)
                    for line in lines[-20:]:
                        print(line.strip())
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        print("=" * 60)
    
    def run(self):
        """Main loop - run the verification system."""
        print("\n" + "=" * 60)
        print("STARTING CAMERA...")
        print("=" * 60)
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Could not open camera!")
            return
        
        # Set camera properties for maximum performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Use MJPG for better performance
        
        print("[OK] Camera initialized successfully!")
        print("\nINSTRUCTIONS:")
        print("1. Press 'C' to capture reference barcode (do this first!)")
        print("2. Press 'S' to start production verification")
        print("3. Press 'S' again to pause verification")
        print("4. Press 'R' to reset reference barcode")
        print("5. Press 'L' to view logs")
        print("6. Press 'Q' to quit\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Could not read from camera!")
                break
            
            # Detect barcodes in current frame
            barcodes = self.detect_barcode(frame)
            
            # Draw barcode overlays
            if barcodes:
                frame = self.draw_overlay(frame, barcodes)
            
            # Draw status panel
            display_frame = self.draw_status_panel(frame)
            
            # Production mode - automatic verification
            if self.production_mode and self.reference_barcode:
                self.verify_product(frame)
            
            # Display frame
            cv2.imshow('Production Line Barcode Verifier', display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                # Quit
                print("\n[SHUTDOWN] Shutting down system...")
                break
            
            elif key == ord('c'):
                # Capture reference barcode
                print("\n[CAPTURE] Capturing reference barcode...")
                self.capture_reference(frame)
            
            elif key == ord('s'):
                # Toggle production mode
                if not self.reference_barcode:
                    print("\n[WARNING] Cannot start production - no reference barcode set!")
                    print("   Press 'C' to capture reference barcode first.")
                    self.play_sound('no_barcode')
                else:
                    self.production_mode = not self.production_mode
                    if self.production_mode:
                        print("\n[START] PRODUCTION MODE STARTED")
                        print(f"   Checking barcodes every {self.scan_interval}s")
                        print(f"   Reference: {self.reference_barcode}")
                        self.last_scan_time = 0  # Reset timer
                    else:
                        print("\n[PAUSE] PRODUCTION MODE PAUSED")
            
            elif key == ord('r'):
                # Reset reference barcode
                print("\n[RESET] Resetting reference barcode...")
                self.reference_barcode = None
                self.reference_type = None
                self.production_mode = False
                print("[OK] Reference barcode cleared. Press 'C' to set new reference.")
            
            elif key == ord('l'):
                # View logs
                self.view_logs()
            
            elif key == ord('h'):
                # Show help
                print("\n" + "=" * 60)
                print("HELP - KEYBOARD CONTROLS")
                print("=" * 60)
                print("C - Capture reference barcode")
                print("S - Start/Stop production verification")
                print("R - Reset reference barcode")
                print("L - View recent logs")
                print("H - Show this help")
                print("Q - Quit system")
                print("=" * 60)
        
        # Cleanup
        self.print_statistics()
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n[OK] System shutdown complete!")
        print(f"Full logs saved to: {self.log_file}")


def main():
    """Entry point."""
    verifier = ProductionLineVerifier()
    verifier.run()


if __name__ == "__main__":
    main()
