"""
Core scanning logic and state management
"""

import logging
import random
import threading
import time
from datetime import datetime
from queue import Queue


logger = logging.getLogger(__name__)


class ScannerState:
    """Manage scanner state and statistics"""
    
    def __init__(self):
        self.running = False
        self.scanning_active = False
        self.reference_barcode = None
        self.stats = {
            'total_scans': 0,
            'matches': 0,
            'mismatches': 0,
            'last_scan': None,
            'last_result': None,
            'session_start': None
        }
        self.gui_queue = Queue()
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'total_scans': 0,
            'matches': 0,
            'mismatches': 0,
            'last_scan': None,
            'last_result': None,
            'session_start': datetime.now() if self.reference_barcode else None
        }
        logger.info("Statistics reset")
    
    def get_stats(self):
        """Get a copy of current statistics"""
        return self.stats.copy()


class BarcodeScanner:
    """Barcode scanner controller"""
    
    def __init__(self, config, state):
        """
        Initialize barcode scanner
        
        Args:
            config: Configuration object
            state: ScannerState object
        """
        self.config = config
        self.state = state
        self.output_file = config.get('Scanner', 'output_file')
        self.scan_interval = config.getfloat('Scanner', 'scan_interval')
        self.simulate = config.getboolean('Scanner', 'simulate_camera')
        self.scan_thread = None
        
        logger.info(f"Scanner initialized (simulate={self.simulate})")
    
    def simulate_scan(self):
        """
        Simulate barcode scanning for testing
        
        Returns:
            str: Simulated barcode
        """
        barcodes = ["123456789", "987654321", "555666777", "111222333"]
        return random.choice(barcodes)
    
    def scan_barcode(self):
        """
        Scan a barcode (real or simulated)
        
        Returns:
            str: Scanned barcode or None
        """
        if self.simulate:
            return self.simulate_scan()
        else:
            # TODO: Implement real camera scanning
            # This is where you'd integrate with your actual barcode scanner
            logger.warning("Real camera scanning not implemented, using simulation")
            return self.simulate_scan()
    
    def register_reference(self):
        """
        Register the reference barcode
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.state.gui_queue.put(('status', 'SCANNING REFERENCE'))
            self.state.gui_queue.put(('log', 'Initiating reference scan...'))
            logger.info("Starting reference barcode registration")
            
            time.sleep(0.5)  # Simulate scan delay
            code = self.scan_barcode()
            
            if code:
                self.state.reference_barcode = code
                self.state.stats['session_start'] = datetime.now()
                
                self.state.gui_queue.put(('reference', code))
                self.state.gui_queue.put(('status', 'REFERENCE LOCKED'))
                self.state.gui_queue.put(('log', f'Reference registered: {code}'))
                
                self.log_to_file(f"REFERENCE REGISTERED: {code}")
                logger.info(f"Reference barcode registered: {code}")
                return True
            else:
                self.state.gui_queue.put(('error', 'SCAN FAILED'))
                self.log_to_file("REFERENCE SCAN FAILED")
                logger.error("Reference barcode scan failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during reference registration: {e}")
            self.state.gui_queue.put(('error', f'Registration error: {str(e)}'))
            return False
    
    def toggle_scanning(self):
        """Toggle continuous scanning on/off"""
        if not self.state.reference_barcode:
            self.state.gui_queue.put(('error', 'NO REFERENCE SET'))
            logger.warning("Attempted to start scanning without reference")
            return False
        
        self.state.scanning_active = not self.state.scanning_active
        
        if self.state.scanning_active:
            self.state.gui_queue.put(('scanning', True))
            self.state.gui_queue.put(('status', 'SCANNING ACTIVE'))
            self.state.gui_queue.put(('log', 'Scanning initiated'))
            
            self.log_to_file("=" * 60)
            self.log_to_file(f"SCANNING STARTED - Reference: {self.state.reference_barcode}")
            self.log_to_file("=" * 60)
            logger.info("Continuous scanning started")
        else:
            self.state.gui_queue.put(('scanning', False))
            self.state.gui_queue.put(('status', 'SCANNING PAUSED'))
            self.state.gui_queue.put(('log', 'Scanning terminated'))
            
            self.log_to_file("=" * 60)
            self.log_to_file("SCANNING STOPPED")
            self.log_to_file("=" * 60)
            logger.info("Continuous scanning stopped")
        
        return True
    
    def compare_and_log(self, scanned_code):
        """
        Compare scanned code with reference and log result
        
        Args:
            scanned_code: The barcode that was scanned
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.state.stats['total_scans'] += 1
            self.state.stats['last_scan'] = scanned_code
            
            if scanned_code == self.state.reference_barcode:
                self.state.stats['matches'] += 1
                self.state.stats['last_result'] = 'MATCH'
                result = 'OK'
                self.state.gui_queue.put(('scan_result', {'code': scanned_code, 'match': True}))
                logger.info(f"Match: {scanned_code}")
            else:
                self.state.stats['mismatches'] += 1
                self.state.stats['last_result'] = 'ERROR'
                result = 'ERROR'
                self.state.gui_queue.put(('scan_result', {'code': scanned_code, 'match': False}))
                logger.warning(f"Mismatch: {scanned_code} (expected {self.state.reference_barcode})")
            
            self.state.gui_queue.put(('stats', self.state.stats.copy()))
            self.log_to_file(f"[{timestamp}] {result}: {scanned_code}")
            
        except Exception as e:
            logger.error(f"Error during scan comparison: {e}")
    
    def log_to_file(self, message):
        """
        Write message to output file
        
        Args:
            message: Message to write
        """
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
    
    def scanning_loop(self):
        """Main scanning loop (runs in separate thread)"""
        logger.info("Scanning loop thread started")
        
        while self.state.running:
            try:
                if self.state.scanning_active:
                    start_time = time.time()
                    
                    code = self.scan_barcode()
                    if code:
                        self.compare_and_log(code)
                    
                    elapsed = time.time() - start_time
                    sleep_time = max(0, self.scan_interval - elapsed)
                    time.sleep(sleep_time)
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in scanning loop: {e}")
                time.sleep(1)  # Prevent tight loop on error
        
        logger.info("Scanning loop thread stopped")
    
    def start(self):
        """Start the scanner background thread"""
        if not self.state.running:
            self.state.running = True
            self.scan_thread = threading.Thread(target=self.scanning_loop, daemon=True)
            self.scan_thread.start()
            logger.info("Scanner background thread started")
    
    def stop(self):
        """Stop the scanner and cleanup"""
        logger.info("Stopping scanner...")
        self.state.running = False
        self.state.scanning_active = False
        
        if self.scan_thread:
            self.scan_thread.join(timeout=2)
        
        logger.info("Scanner stopped")

