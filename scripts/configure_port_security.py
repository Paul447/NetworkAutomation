"""
Port Security Configuration Script

Automates port security setup on a Cisco switch via serial/console connection.
Port security restricts which MAC addresses are allowed on a switchport to
prevent unauthorized devices from connecting to the network.

Features configured per interface:
  - Maximum allowed MAC addresses
  - Sticky MAC learning (the switch learns and remembers connected MACs automatically)
  - Violation mode: what happens when an unauthorized MAC is detected
      shutdown  - disables the port (default, most secure)
      restrict  - drops frames and logs a violation, port stays up
      protect   - silently drops frames, no log
  - Optional: manually pin a specific trusted MAC address

Requirements:
  - USB-to-serial console cable connected to the switch
  - Run scripts/find_serial_ports.py to find the correct port (e.g. /dev/tty.usbserial-1130)
  - Update the 'port' value in the device dictionary below before running
  - Interfaces must be in access mode (not trunk) for port security to apply

Usage:
    python scripts/configure_port_security.py
"""

from netmiko import ConnectHandler

# Device connection parameters.
# Update 'port' to match your USB-to-serial adapter (run find_serial_ports.py to check).
device = {
    "device_type": "cisco_ios_serial",
    "serial_settings": {
        "port": "/dev/tty.usbserial-1130",
        "baudrate": 9600,
    },
    # Uncomment and fill in if the device requires credentials:
    # "username": "admin",
    # "password": "ABcd1234!",
    # "secret": "ABcd1234!",
}

VALID_VIOLATION_MODES = ("shutdown", "restrict", "protect")


def configure_port_security_on_interface(conn, interface):
    """Apply port security settings to a single switchport interface."""

    print(f"\n--- Configuring port security on {interface} ---")

    # Maximum MAC addresses allowed on this port.
    max_macs = input("  Max allowed MAC addresses (default 1): ").strip()
    if not max_macs:
        max_macs = "1"

    # Violation mode.
    print("  Violation modes: shutdown | restrict | protect")
    violation_mode = input("  Violation mode (default: shutdown): ").strip().lower()
    if violation_mode not in VALID_VIOLATION_MODES:
        print(f"  Invalid mode, defaulting to 'shutdown'.")
        violation_mode = "shutdown"

    # Build base port-security commands.
    commands = [
        f"interface {interface}",
        "switchport mode access",
        "switchport port-security",
        f"switchport port-security maximum {max_macs}",
        "switchport port-security mac-address sticky",
        f"switchport port-security violation {violation_mode}",
    ]

    # Optionally pin a specific trusted MAC address.
    static_mac = input("  Pin a specific trusted MAC address? (leave blank to skip): ").strip()
    if static_mac:
        commands.append(f"switchport port-security mac-address {static_mac}")
        print(f"  Pinning MAC {static_mac} to {interface}.")

    conn.send_config_set(commands)
    print(f"  Port security applied to {interface}: max={max_macs}, violation={violation_mode}, sticky=enabled.")


with ConnectHandler(**device) as conn:
    conn.enable()

    # -- Interfaces to secure ------------------------------------------------------
    raw_interfaces = input(
        "Enter interface(s) to secure, comma-separated (e.g. fa0/1, fa0/2, gi0/1): "
    ).strip()
    interfaces = [iface.strip() for iface in raw_interfaces.split(",") if iface.strip()]

    if not interfaces:
        print("No interfaces specified. Exiting.")
    else:
        for interface in interfaces:
            configure_port_security_on_interface(conn, interface)

        # -- Save configuration --------------------------------------------------------
        conn.save_config()
        print("\nPort security configuration saved successfully.")
