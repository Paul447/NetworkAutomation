"""
configure_port_security.py
--------------------------
Automates port security configuration on Cisco switchport interfaces via serial/console.

Port security restricts which MAC addresses are allowed on a switchport.
If an unauthorized device connects, the switch takes a configured action
(shut the port down, drop frames, or silently discard) depending on the
violation mode chosen.

What this script does:
  1. Connects to the switch over a USB-to-serial console cable using netmiko
  2. Enters privileged exec mode (enable)
  3. Prompts for a comma-separated list of interfaces to secure
  4. For each interface, interactively configures:
       - switchport mode access        (required for port security)
       - switchport port-security      (enables the feature)
       - maximum allowed MAC addresses (default: 1)
       - sticky MAC learning           (switch auto-learns and saves connected MACs)
       - violation mode                (shutdown | restrict | protect)
       - optional static trusted MAC   (manually pinned)
  5. Saves the running configuration to NVRAM

Violation modes explained:
  shutdown  — Port is err-disabled immediately. Most secure. Port must be
              manually re-enabled after a violation ('shutdown' → 'no shutdown').
  restrict  — Unauthorized frames are dropped and a syslog message is generated.
              Port stays up so legitimate traffic is unaffected.
  protect   — Unauthorized frames are silently dropped. No log entry created.
              Use only when silent enforcement is acceptable.

Before running:
  - Interfaces must be access ports (not trunks) for port security to apply
  - Run scripts/find_serial_ports.py to find your port (e.g. /dev/tty.usbserial-1130)
  - Update the 'port' value in the device dictionary below
  - Uncomment username/password/secret below if the device requires them

Usage:
    python scripts/configure_port_security.py
"""

from netmiko import ConnectHandler

# ---------------------------------------------------------------------------
# Device connection parameters
# Update 'port' to match your USB-to-serial adapter.
# Run scripts/find_serial_ports.py to find the correct value.
# ---------------------------------------------------------------------------
device = {
    "device_type": "cisco_ios_serial",
    "serial_settings": {
        "port": "/dev/tty.usbserial-1130",  # <-- update this
        "baudrate": 9600,                   # default for Cisco console ports
    },
    # Uncomment if the device requires authentication:
    # "username": "admin",
    # "password": "ABcd1234!",
    # "secret":   "ABcd1234!",  # enable/privileged exec password
}

VALID_VIOLATION_MODES = ("shutdown", "restrict", "protect")


def configure_port_security_on_interface(conn, interface: str) -> None:
    """
    Apply port security settings to a single switchport interface.

    Args:
        conn:      Active netmiko ConnectHandler session.
        interface: Interface name as shown in IOS (e.g. 'fa0/1', 'gi0/1').
    """
    print(f"\n--- Configuring port security on {interface} ---")

    # -- Maximum MAC addresses ---------------------------------------------------
    # Limits how many MACs can be learned/allowed on this port.
    # Default of 1 is correct for end-user access ports (one device per port).
    max_macs = input("  Max allowed MAC addresses (default 1): ").strip()
    if not max_macs:
        max_macs = "1"

    # -- Violation mode ----------------------------------------------------------
    print("  Violation modes: shutdown | restrict | protect")
    violation_mode = input("  Violation mode (default: shutdown): ").strip().lower()
    if violation_mode not in VALID_VIOLATION_MODES:
        print("  Invalid mode — defaulting to 'shutdown'.")
        violation_mode = "shutdown"

    # -- Build IOS commands ------------------------------------------------------
    commands = [
        f"interface {interface}",
        "switchport mode access",                       # port security requires access mode
        "switchport port-security",                     # enable port security on this interface
        f"switchport port-security maximum {max_macs}",
        "switchport port-security mac-address sticky",  # auto-learn and persist MACs
        f"switchport port-security violation {violation_mode}",
    ]

    # -- Optional: static trusted MAC --------------------------------------------
    # Manually pins a specific MAC to this port in addition to sticky learning.
    # Useful for locking a known device (e.g. a server or printer) to a port.
    static_mac = input("  Pin a specific trusted MAC address? (leave blank to skip): ").strip()
    if static_mac:
        commands.append(f"switchport port-security mac-address {static_mac}")
        print(f"  Pinning MAC {static_mac} to {interface}.")

    conn.send_config_set(commands)
    print(f"  Port security applied to {interface}: "
          f"max={max_macs}, violation={violation_mode}, sticky=enabled.")


with ConnectHandler(**device) as conn:

    # Enter privileged exec mode so we can make configuration changes.
    conn.enable()

    # -- Interface selection -----------------------------------------------------
    raw_interfaces = input(
        "Enter interface(s) to secure, comma-separated (e.g. fa0/1, fa0/2, gi0/1): "
    ).strip()
    interfaces = [iface.strip() for iface in raw_interfaces.split(",") if iface.strip()]

    if not interfaces:
        print("No interfaces specified. Exiting.")
    else:
        for interface in interfaces:
            configure_port_security_on_interface(conn, interface)

        # -- Save configuration --------------------------------------------------
        # Writes the running config to startup config (NVRAM) so it survives reboot.
        conn.save_config()
        print("\nPort security configuration saved successfully.")
