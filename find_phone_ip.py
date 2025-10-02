#!/usr/bin/env python3
"""
Script to find your phone's IP address for IP Webcam
"""

import subprocess
import socket
import threading
import time

def scan_ip(ip, port=8080):
    """Check if IP Webcam or DroidCam is running on this IP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return True
    except:
        pass
    return False

def main():
    print("=" * 60)
    print("FINDING YOUR PHONE'S IP ADDRESS FOR DROIDCAM/IP WEBCAM")
    print("=" * 60)
    print("Make sure:")
    print("1. Your phone is connected to the same WiFi as Raspberry Pi")
    print("2. DroidCam app is installed and running on your phone")
    print("3. DroidCam server is started (tap 'Start' in DroidCam)")
    print("=" * 60)
    
    # Get Raspberry Pi's network
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        pi_ip = result.stdout.strip().split()[0]
        network = '.'.join(pi_ip.split('.')[:-1]) + '.'
        print(f"Raspberry Pi IP: {pi_ip}")
        print(f"Scanning network: {network}x")
        print("Scanning for IP Webcam servers...")
    except:
        print("Could not determine network. Scanning common ranges...")
        networks = ["192.168.0.", "192.168.1.", "10.0.0."]
    
    found_phones = []
    
    # Scan for DroidCam (port 4747) and IP Webcam (port 8080)
    for network_base in [f"192.168.0.{i}" for i in range(100, 110)]:
        # Check DroidCam port 4747
        if scan_ip(network_base, 4747):
            found_phones.append(f"{network_base}:4747")
            print(f"✓ Found DroidCam at: {network_base}:4747")
        # Check IP Webcam port 8080
        if scan_ip(network_base, 8080):
            found_phones.append(f"{network_base}:8080")
            print(f"✓ Found IP Webcam at: {network_base}:8080")
    
    if found_phones:
        print("\n" + "=" * 60)
        print("FOUND PHONE CAMERAS!")
        print("=" * 60)
        for phone_ip in found_phones:
            ip, port = phone_ip.split(':')
            print(f"Phone IP: {phone_ip}")
            if port == "4747":
                print(f"Video URL: http://{phone_ip}/video")
                print(f"Alternative: http://{phone_ip}/mjpegfeed?640x480")
                print(f"Web interface: http://{phone_ip}")
            else:
                print(f"Video URL: http://{phone_ip}/video")
                print(f"Web interface: http://{phone_ip}")
        print("\nTo use with barcode system:")
        print("1. Copy one of the video URLs above")
        print("2. Update the camera_sources list in production_line_verifier_BARCODE.py")
        print("3. Run the barcode system")
    else:
        print("\n" + "=" * 60)
        print("NO PHONE CAMERAS FOUND")
        print("=" * 60)
        print("Make sure:")
        print("1. DroidCam app is installed on your phone")
        print("2. DroidCam server is running (tap 'Start' in DroidCam)")
        print("3. Phone is on the same WiFi network")
        print("4. Check your phone's IP address in DroidCam app")
        print("\nYou can also run the barcode system in demo mode!")

if __name__ == "__main__":
    main()
