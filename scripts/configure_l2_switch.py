"""
configure_l2_switch.py
----------------------
Automates base configuration for a Cisco Layer 2 switch via serial/console.

What this script does (in order):
  1. Connects to the switch over a USB-to-serial console cable using netmiko
  2. Enters privileged exec mode (enable)
  3. Prompts for a hostname and sets it on the device
  4. Applies configs/base_config.txt — sets domain name, local credentials,
     console password, enable secret, and service password-encryption
  5. Interactively creates VLANs (user provides VLAN ID, name, description)
  6. Saves the running configuration to NVRAM (write memory)

Before running:
  - Run scripts/find_serial_ports.py to find your port (e.g. /dev/tty.usbserial-1130)
  - Update the 'port' value in the device dictionary below
  - Edit configs/base_config.txt to match your credentials and domain name
  - Uncomment username/password/secret below if the device requires them

Usage:
    python scripts/configure_l2_switch.py
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

with ConnectHandler(**device) as conn:

    # Enter privileged exec mode so we can make configuration changes.
    conn.enable()

    # -- Hostname ----------------------------------------------------------------
    hostname = input("Hostname for this device: ").strip()
    conn.send_config_set([f"hostname {hostname}"])

    # After changing the hostname the CLI prompt changes (e.g. Switch# → Core01#).
    # set_base_prompt() reads the new prompt so netmiko doesn't time out waiting
    # for the old one.
    conn.set_base_prompt()

    # -- Base configuration ------------------------------------------------------
    # Sends every line in base_config.txt as a config command.
    # Covers: domain name, local user, console password, enable secret,
    # and service password-encryption.
    output = conn.send_config_from_file("configs/base_config.txt")
    print(output)

    # -- VLAN creation -----------------------------------------------------------
    vlan_count = int(input("How many VLANs do you want to create? "))
    for i in range(vlan_count):
        confirm = input(f"Create VLAN {i + 1}? (y/n): ").strip().lower()
        if confirm != "y":
            continue

        vlan_id     = input("  VLAN ID: ").strip()
        vlan_name   = input("  VLAN name: ").strip()
        description = input("  Description: ").strip()

        conn.send_config_set([
            f"vlan {vlan_id}",
            f"name {vlan_name}",
            f"interface vlan {vlan_id}",
            f"description {description}",
        ])
        print(f"  VLAN {vlan_id} ({vlan_name}) created.")

    # -- Save configuration ------------------------------------------------------
    # Writes the running config to startup config (NVRAM) so it survives reboot.
    conn.save_config()
    print("Configuration saved successfully.")
