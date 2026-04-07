"""
connection_handler.py
---------------------
Interactive connection builder for Cisco IOS devices.

Asks the user how they want to connect, gathers the required details,
and returns a ready-to-use netmiko ConnectHandler session.

Supported connection types:
  1. Physical (serial/console) — USB-to-serial console cable
  2. Telnet                    — IP-based telnet connection

This module is designed to be imported by other scripts:

    from scripts.connection_handler import get_connection

    with get_connection() as conn:
        conn.enable()
        ...

It can also be run directly to test that a connection succeeds:

    python scripts/connection_handler.py
"""

import glob
from netmiko import ConnectHandler


# ── Connection type constants ────────────────────────────────────────────────
PHYSICAL = "1"
TELNET   = "2"


# ════════════════════════════════════════════════════════════════════════════
#  Serial port discovery
# ════════════════════════════════════════════════════════════════════════════

def _find_serial_ports() -> list[str]:
    """Return a list of available serial/TTY ports on the system."""
    return glob.glob("/dev/tty.*")          # macOS
    # Linux: glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyS*")


def _select_serial_port() -> str:
    """
    Auto-discover serial ports and let the user pick one.

    Returns:
        The selected port path (e.g. '/dev/tty.usbserial-1130').

    Raises:
        SystemExit: if no serial ports are found.
    """
    ports = _find_serial_ports()

    if not ports:
        print("\n[!] No serial ports found.")
        print("    Make sure your USB-to-serial cable is connected and try again.")
        raise SystemExit(1)

    if len(ports) == 1:
        print(f"\n    Found serial port: {ports[0]}")
        return ports[0]

    # Multiple ports — let the user choose
    print("\n    Available serial ports:")
    for i, port in enumerate(ports, start=1):
        print(f"      [{i}] {port}")

    while True:
        choice = input(f"    Select port (1-{len(ports)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ports):
            return ports[int(choice) - 1]
        print(f"    Invalid choice. Enter a number between 1 and {len(ports)}.")


# ════════════════════════════════════════════════════════════════════════════
#  Credential prompt
# ════════════════════════════════════════════════════════════════════════════

def _ask_credentials() -> dict:
    """
    Ask the user whether the device requires a username and/or password.

    Returns:
        A dict with any of: 'username', 'password', 'secret'.
        Only keys the user actually provided are included.
    """
    import getpass

    creds = {}

    has_username = input("\n    Does the device require a username? (y/n): ").strip().lower()
    if has_username == "y":
        creds["username"] = input("    Username: ").strip()

    has_password = input("    Does the device require a password? (y/n): ").strip().lower()
    if has_password == "y":
        creds["password"] = getpass.getpass("    Password: ")

    has_secret = input("    Does the device require an enable secret? (y/n): ").strip().lower()
    if has_secret == "y":
        creds["secret"] = getpass.getpass("    Enable secret: ")

    return creds


# ════════════════════════════════════════════════════════════════════════════
#  Connection builders
# ════════════════════════════════════════════════════════════════════════════

def _build_physical_device() -> dict:
    """
    Gather parameters for a physical serial/console connection.

    Returns:
        A netmiko device dict ready for ConnectHandler.
    """
    print("\n── Physical (Serial/Console) Connection ─────────────────────────")

    port = _select_serial_port()

    baudrate_input = input(
        "\n    Baud rate (press Enter for default 9600): "
    ).strip()
    baudrate = int(baudrate_input) if baudrate_input.isdigit() else 9600

    device = {
        "device_type": "cisco_ios_serial",
        "serial_settings": {
            "port":     port,
            "baudrate": baudrate,
        },
    }

    device.update(_ask_credentials())
    return device


def _build_telnet_device() -> dict:
    """
    Gather parameters for a Telnet connection.

    Returns:
        A netmiko device dict ready for ConnectHandler.
    """
    print("\n── Telnet Connection ─────────────────────────────────────────────")

    host = input("\n    IP address of the device: ").strip()

    port_input = input("    Telnet port (press Enter for default 23): ").strip()
    port = int(port_input) if port_input.isdigit() else 23

    device = {
        "device_type": "cisco_ios_telnet",
        "host":         host,
        "port":         port,
    }

    device.update(_ask_credentials())
    return device


# ════════════════════════════════════════════════════════════════════════════
#  Public API
# ════════════════════════════════════════════════════════════════════════════

def get_device_params() -> dict:
    """
    Interactively build a netmiko device parameter dictionary.

    Asks the user which connection type they want (physical or telnet),
    then collects the required details for that type.

    Returns:
        A dict suitable for passing to netmiko's ConnectHandler.
    """
    print("\n╔══════════════════════════════════════════╗")
    print("║     Network Automation — Connect         ║")
    print("╚══════════════════════════════════════════╝")
    print("\n  How do you want to connect to the device?")
    print("    [1] Physical connection (serial/console cable)")
    print("    [2] Telnet (IP address)")

    while True:
        choice = input("\n  Your choice (1 or 2): ").strip()
        if choice in (PHYSICAL, TELNET):
            break
        print("  Invalid choice. Enter 1 or 2.")

    if choice == PHYSICAL:
        return _build_physical_device()
    else:
        return _build_telnet_device()


def get_connection() -> ConnectHandler:
    """
    Interactively gather connection details and return an open netmiko session.

    Intended to be used as a context manager:

        with get_connection() as conn:
            conn.enable()
            output = conn.send_command("show version")

    Returns:
        An active netmiko ConnectHandler instance.
    """
    device = get_device_params()

    print("\n  Connecting to device...")
    conn = ConnectHandler(**device)
    print("  Connected.\n")
    return conn


# ════════════════════════════════════════════════════════════════════════════
#  Standalone test
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    with get_connection() as conn:
        conn.enable()
        output = conn.send_command("show version")
        print(output)
