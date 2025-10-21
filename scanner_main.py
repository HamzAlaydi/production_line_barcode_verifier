#!/usr/bin/env python3
"""
Nexus Barcode Scanner - Main Entry Point
Production-ready barcode scanner with futuristic GUI

Run this file to start the scanner application.
"""

import logging
import sys
import tkinter as tk
from datetime import datetime

# Import local modules
from src.utils import Config, setup_logging, ensure_directories, validate_environment, Theme
from src.scanner import ScannerState, BarcodeScanner
from src.gui import ScannerGUI


def main():
    """Main application entry point"""
    try:
        # Ensure directories exist
        ensure_directories()
        
        # Load configuration
        config = Config('config/config.ini')
        
        # Setup logging
        logger = setup_logging(config)
        logger.info("=" * 60)
        logger.info("NEXUS BARCODE SCANNER - Starting")
        logger.info("=" * 60)
        
        # Validate environment
        is_valid, error_msg = validate_environment()
        if not is_valid:
            logger.error(f"Environment validation failed:\n{error_msg}")
            print(f"ERROR: Environment validation failed:\n{error_msg}")
            return 1
        
        # Initialize theme
        theme = Theme(config)
        logger.info("Theme loaded")
        
        # Initialize scanner state
        state = ScannerState()
        logger.info("Scanner state initialized")
        
        # Initialize barcode scanner
        scanner = BarcodeScanner(config, state)
        
        # Initialize output file
        output_file = config.get('Scanner', 'output_file')
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: {'Simulated' if config.getboolean('Scanner', 'simulate_camera') else 'Production'}\n")
            f.write("=" * 60 + "\n")
        
        # Start scanner background thread
        scanner.start()
        state.gui_queue.put(('log', 'System initialized - Ready'))
        
        # Create GUI
        root = tk.Tk()
        app = ScannerGUI(root, config, theme, scanner, state)
        
        logger.info("GUI created, starting main loop")
        print("\n" + "=" * 60)
        print("  ◢ NEXUS SCANNER - Production Ready")
        print("=" * 60)
        print(f"  Screen: {config.getint('Display', 'screen_width')}x{config.getint('Display', 'screen_height')}")
        print(f"  Mode: {'Simulation' if config.getboolean('Scanner', 'simulate_camera') else 'Production'}")
        print(f"  Logs: {config.get('Logging', 'log_file')}")
        print("=" * 60)
        print("\n  Press ESC to exit, F11 for fullscreen\n")
        
        # Run GUI
        try:
            root.mainloop()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            print("\nShutting down...")
        finally:
            cleanup(scanner, state, logger)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Please ensure config/config.ini exists")
        return 1
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cleanup(scanner, state, logger):
    """Cleanup resources"""
    logger.info("Cleaning up resources...")
    
    # Stop scanner
    scanner.stop()
    
    # Final log entry
    output_file = scanner.output_file
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total scans: {state.stats['total_scans']}\n")
        f.write(f"Matches: {state.stats['matches']}\n")
        f.write(f"Errors: {state.stats['mismatches']}\n")
        f.write("=" * 60 + "\n")
    
    logger.info("Cleanup complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    sys.exit(main())

