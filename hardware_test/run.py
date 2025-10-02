#!/usr/bin/env python3
"""
Quick start script for hardware test application
Provides easy access to common operations
"""

import sys
import subprocess
import os

def run_main_app(simulator=False):
    """Run the main application"""
    cmd = [sys.executable, "main.py"]
    if simulator:
        cmd.append("--simulator")
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

def run_test():
    """Run hardware test"""
    cmd = [sys.executable, "test_setup.py"]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

def show_help():
    """Show help message"""
    print("Hardware Test Application - Quick Start")
    print("=" * 40)
    print("Usage: python3 run.py [command]")
    print()
    print("Commands:")
    print("  start       Start the application with real hardware")
    print("  sim         Start the application with simulator")
    print("  test        Run hardware setup test")
    print("  help        Show this help message")
    print()
    print("Examples:")
    print("  python3 run.py start    # Run with real hardware")
    print("  python3 run.py sim      # Run with simulator")
    print("  python3 run.py test     # Test hardware setup")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        run_main_app(simulator=False)
    elif command == "sim":
        run_main_app(simulator=True)
    elif command == "test":
        run_test()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
