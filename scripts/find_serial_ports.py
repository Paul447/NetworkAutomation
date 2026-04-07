"""
find_serial_ports.py
--------------------
Utility script to list all serial/TTY ports currently available on the system.

Run this before any configuration script to identify the correct port name for
your USB-to-serial console cable (e.g. /dev/tty.usbserial-1130 on macOS,
/dev/ttyUSB0 on Linux).

Usage:
    python scripts/find_serial_ports.py

Example output:
    Available serial ports:
      /dev/tty.usbserial-1130
      /dev/tty.Bluetooth-Incoming-Port
"""

import glob


def find_serial_ports() -> None:
    """Print all serial/TTY ports detected on the system."""
    ports = glob.glob("/dev/tty.*")
    if ports:
        print("Available serial ports:")
        for port in ports:
            print(f"  {port}")
    else:
        print("No serial ports found. Check your USB-to-serial cable connection.")


if __name__ == "__main__":
    find_serial_ports()
