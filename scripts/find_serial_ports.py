"""
Utility script to discover available serial/TTY ports on the system.
Run this before configuring a device to find the correct port name
(e.g. /dev/tty.usbserial-1130) to use in the configuration scripts.

Usage:
    python scripts/find_serial_ports.py
"""

import glob


def find_serial_ports():
    ports = glob.glob("/dev/tty.*")
    if ports:
        print("Available serial ports:")
        for port in ports:
            print(f"  {port}")
    else:
        print("No serial ports found. Check your USB-to-serial cable connection.")


if __name__ == "__main__":
    find_serial_ports()
