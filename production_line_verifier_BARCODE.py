#!/usr/bin/env python3
"""
Production Line BARCODE (1D) Verification System
Optimized specifically for traditional barcodes (CODE128, EAN13, UPC-A, etc.)

Keyboard Controls:
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
import winsound


class BarcodeProductionVerifier:
    """Barcode-optimized verification system for production line quality control."""
    
    def __init__(self):
        self.reference_barcode = None
        self.reference_type = None
        self.production_mode = False
        self.log_file = "production_log_barcode.csv"
        
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
        
        print("Production Line BARCODE Verification System - ENHANCED")
        print("=" * 60)
        print("SUPPORTS ALL TRADITIONAL 1D BARCODES:")
        print("  UPC-A, UPC-E, EAN-13, EAN-8")
        print("  Code 39, Code 128, ITF, Codabar")
        print("  MSI, Pharmacode, GS1 DataBar")
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
                winsound.Beep(1000, 100)
            elif sound_type == 'mismatch':
                winsound.Beep(800, 200)
                time.sleep(0.1)
                winsound.Beep(800, 200)
            elif sound_type == 'no_barcode':
                winsound.Beep(400, 500)
            elif sound_type == 'reference_captured':
                winsound.Beep(600, 100)
                time.sleep(0.05)
                winsound.Beep(800, 100)
                time.sleep(0.05)
                winsound.Beep(1000, 100)
        except Exception as e:
            pass
    
    def preprocess_for_barcode(self, frame):
        """
        ADVANCED preprocessing for ALL 1D barcode types.
        Optimized for: UPC-A, UPC-E, EAN-13, EAN-8, Code 39, Code 128,
        ITF, Codabar, MSI, Pharmacode, GS1 DataBar, and more.
        """
        results = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Always include original grayscale
        results.append(gray)
        
        # Method 1: Multiple Adaptive Thresholding (critical for varying lighting)
        for block_size in [11, 15, 19, 25]:
            for c_value in [2, 5, 10]:
                try:
                    adaptive = cv2.adaptiveThreshold(
                        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                        cv2.THRESH_BINARY, block_size, c_value
                    )
                    results.append(adaptive)
                except:
                    pass
        
        # Method 2: Otsu's Thresholding (automatic optimal threshold)
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results.append(otsu)
        
        # Method 3: Inverted Otsu (for reverse contrast barcodes)
        _, otsu_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        results.append(otsu_inv)
        
        # Method 4: CLAHE with multiple settings (High Contrast Enhancement)
        for clip_limit in [2.0, 3.0, 4.0]:
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            results.append(enhanced)
            
            # Also try thresholding after CLAHE
            _, clahe_thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            results.append(clahe_thresh)
        
        # Method 5: Multi-scale Sharpening (critical for blurry barcodes)
        sharpen_kernels = [
            np.array([[-1, -1, -1], [-1,  9, -1], [-1, -1, -1]]),  # Standard
            np.array([[0, -1, 0], [-1,  5, -1], [0, -1, 0]]),      # Mild
            np.array([[-1, -1, -1, -1, -1],
                      [-1,  2,  2,  2, -1],
                      [-1,  2,  8,  2, -1],
                      [-1,  2,  2,  2, -1],
                      [-1, -1, -1, -1, -1]]) / 8.0                  # Strong
        ]
        for kernel in sharpen_kernels:
            sharpened = cv2.filter2D(gray, -1, kernel)
            results.append(sharpened)
        
        # Method 6: Multiple Binary Thresholds (for different barcode contrasts)
        for thresh_val in [100, 127, 150, 180]:
            _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
            results.append(binary)
            _, binary_inv = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
            results.append(binary_inv)
        
        # Method 7: Morphological Operations (clean barcode lines)
        kernel_sizes = [(2, 2), (3, 3), (5, 1), (1, 5)]  # Various including horizontal/vertical
        for ksize in kernel_sizes:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize)
            # Closing (fill gaps)
            closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            results.append(closed)
            # Opening (remove noise)
            opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            results.append(opened)
        
        # Method 8: Gradient-based edge enhancement (critical for thin lines)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel = np.sqrt(sobelx**2 + sobely**2)
        sobel = np.uint8(sobel * 255 / np.max(sobel))
        results.append(sobel)
        
        # Method 9: Gaussian blur then threshold (reduce noise)
        for blur_size in [3, 5]:
            blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
            _, blur_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            results.append(blur_thresh)
        
        # Method 10: Bilateral filter (preserve edges, reduce noise)
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        results.append(bilateral)
        _, bilateral_thresh = cv2.threshold(bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results.append(bilateral_thresh)
        
        # Method 11: Histogram equalization variations
        equalized = cv2.equalizeHist(gray)
        results.append(equalized)
        _, eq_thresh = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results.append(eq_thresh)
        
        # Method 12: Contrast stretching (normalize intensity)
        normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        results.append(normalized)
        
        return results
    
    def detect_barcode(self, frame):
        """
        Enhanced barcode detection for ALL 1D barcode types.
        Handles: UPC, EAN, Code 39, Code 128, ITF, Codabar, MSI, Pharmacode, GS1 DataBar.
        Balanced for accuracy and speed.
        """
        all_barcodes = []
        seen_data = set()
        
        # Function to add unique barcode
        def add_unique_barcode(barcode):
            try:
                data = barcode.data.decode('utf-8')
                if data and data not in seen_data and len(data) > 0:
                    seen_data.add(data)
                    all_barcodes.append(barcode)
                    return True
            except:
                pass
            return False
        
        # STAGE 1: Quick attempts on original and grayscale
        try:
            # Try original color
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # Try grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = pyzbar.decode(gray)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # Try enhanced
            enhanced = cv2.equalizeHist(gray)
            barcodes = pyzbar.decode(enhanced)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
        except:
            pass
        
        # STAGE 2: Try key preprocessing methods (most effective ones)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        try:
            # Otsu's thresholding
            _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            barcodes = pyzbar.decode(otsu)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # Adaptive thresholding
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY, 11, 2)
            barcodes = pyzbar.decode(adaptive)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            clahe_img = clahe.apply(gray)
            barcodes = pyzbar.decode(clahe_img)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
            
            # Sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(gray, -1, kernel)
            barcodes = pyzbar.decode(sharpened)
            for barcode in barcodes:
                if add_unique_barcode(barcode):
                    return all_barcodes
        except:
            pass
        
        # STAGE 3: Try multiple scales (for small/distant barcodes)
        if not all_barcodes:
            for scale in [1.5, 2.0, 0.75]:
                try:
                    width = int(frame.shape[1] * scale)
                    height = int(frame.shape[0] * scale)
                    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
                    
                    barcodes = pyzbar.decode(resized)
                    for barcode in barcodes:
                        if add_unique_barcode(barcode):
                            return all_barcodes
                except:
                    pass
        
        # STAGE 4: Try more preprocessing methods if still nothing found
        if not all_barcodes:
            try:
                # Binary thresholding with different values
                for thresh_val in [127, 150, 100]:
                    _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
                    barcodes = pyzbar.decode(binary)
                    for barcode in barcodes:
                        if add_unique_barcode(barcode):
                            return all_barcodes
                
                # Inverted binary
                _, binary_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                barcodes = pyzbar.decode(binary_inv)
                for barcode in barcodes:
                    if add_unique_barcode(barcode):
                        return all_barcodes
                
                # Morphological operations
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
                morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
                barcodes = pyzbar.decode(morph)
                for barcode in barcodes:
                    if add_unique_barcode(barcode):
                        return all_barcodes
            except:
                pass
        
        return all_barcodes
    
    def capture_reference(self, frame):
        """Capture and store reference barcode from current frame."""
        barcodes = self.detect_barcode(frame)
        
        if not barcodes:
            print("[ERROR] No barcode detected! Please position product correctly and try again.")
            print("TIPS: Ensure good lighting, hold barcode steady, try different angles")
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
        cv2.rectangle(overlay, (0, 0), (width, 220), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display, 0.3, 0, display)
        
        # Title
        cv2.putText(display, "BARCODE VERIFIER - ENHANCED (ALL 1D TYPES)", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Reference barcode status
        if self.reference_barcode:
            ref_text = f"Reference: {self.reference_barcode} ({self.reference_type})"
            cv2.putText(display, ref_text, (20, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(display, "Reference: NOT SET - Press 'C' to capture", 
                       (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Production mode status
        if self.production_mode:
            mode_text = "Mode: PRODUCTION ACTIVE"
            mode_color = (0, 255, 0)
        else:
            mode_text = "Mode: STANDBY - Press 'S' to start"
            mode_color = (255, 255, 0)
        cv2.putText(display, mode_text, (20, 115), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
        
        # Statistics
        stats_text = f"Scans: {self.stats['total_scans']} | Pass: {self.stats['passed']} | Mismatch: {self.stats['mismatched']} | No Barcode: {self.stats['no_barcode']}"
        cv2.putText(display, stats_text, (20, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Performance
        if self.stats['total_scans'] > 0:
            pass_rate = (self.stats['passed'] / self.stats['total_scans']) * 100
            perf_text = f"Pass Rate: {pass_rate:.1f}%"
            cv2.putText(display, perf_text, (20, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Tips for barcode detection
        cv2.putText(display, "Enhanced detection with multi-scale & preprocessing", 
                   (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # Controls
        controls_y = height - 30
        cv2.putText(display, "Controls: C=Capture | S=Start/Stop | R=Reset | L=Logs | Q=Quit", 
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
                if len(lines) > 0:
                    print(lines[0].strip())
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
        print("6. Press 'Q' to quit")
        print("\nBARCODE TIPS:")
        print("- Hold barcode flat and steady")
        print("- Ensure good, even lighting")
        print("- Avoid glare and shadows")
        print("- Keep barcode 15-30 cm from camera")
        print("- Try different angles if not detecting\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Could not read from camera!")
                break
            
            # Always detect barcodes for visual feedback
            # Use lightweight detection for display
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply basic enhancement
            enhanced = cv2.equalizeHist(gray)
            
            # Try multiple quick methods for display
            barcodes = pyzbar.decode(frame)
            if not barcodes:
                barcodes = pyzbar.decode(gray)
            if not barcodes:
                barcodes = pyzbar.decode(enhanced)
            
            # Draw barcode overlays
            if barcodes:
                frame = self.draw_overlay(frame, barcodes)
            
            # Draw status panel
            display_frame = self.draw_status_panel(frame)
            
            # Production mode - automatic verification
            if self.production_mode and self.reference_barcode:
                self.verify_product(frame)
            
            # Display frame
            cv2.imshow('Barcode Verifier Enhanced - All 1D Types', display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n[SHUTDOWN] Shutting down system...")
                break
            
            elif key == ord('c'):
                print("\n[CAPTURE] Capturing reference barcode...")
                self.capture_reference(frame)
            
            elif key == ord('s'):
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
                        self.last_scan_time = 0
                    else:
                        print("\n[PAUSE] PRODUCTION MODE PAUSED")
            
            elif key == ord('r'):
                print("\n[RESET] Resetting reference barcode...")
                self.reference_barcode = None
                self.reference_type = None
                self.production_mode = False
                print("[OK] Reference barcode cleared. Press 'C' to set new reference.")
            
            elif key == ord('l'):
                self.view_logs()
            
            elif key == ord('h'):
                print("\n" + "=" * 60)
                print("HELP - KEYBOARD CONTROLS")
                print("=" * 60)
                print("C - Capture reference barcode")
                print("S - Start/Stop production verification")
                print("R - Reset reference barcode")
                print("L - View recent logs")
                print("H - Show this help")
                print("Q - Quit system")
                print("\nBARCODE DETECTION TIPS:")
                print("- Use good, even lighting (avoid shadows)")
                print("- Hold barcode flat and parallel to camera")
                print("- Keep barcode at 15-30 cm distance")
                print("- Avoid glare on barcode surface")
                print("- Try rotating slightly if not detecting")
                print("=" * 60)
        
        # Cleanup
        self.print_statistics()
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n[OK] System shutdown complete!")
        print(f"Full logs saved to: {self.log_file}")


def main():
    """Entry point."""
    verifier = BarcodeProductionVerifier()
    verifier.run()


if __name__ == "__main__":
    main()

