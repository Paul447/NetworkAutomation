"""
Layer 2 Switch Configuration Script

Automates basic L2 switch setup via a serial/console connection:
  - Sets the device hostname
  - Applies base config from configs/base_config.txt
    (domain name, local user, console/enable passwords, service password-encryption)
  - Creates VLANs interactively (user provides VLAN ID, name, and description)
  - Saves the running configuration

Requirements:
  - USB-to-serial console cable connected to the switch
  - Run scripts/find_serial_ports.py to find the correct port (e.g. /dev/tty.usbserial-1130)
  - Update the 'port' value in the device dictionary below before running

Usage:
    python scripts/configure_l2_switch.py
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

with ConnectHandler(**device) as conn:
    conn.enable()

    # -- Hostname ------------------------------------------------------------------
    hostname = input("Hostname for this device: ").strip()
    conn.send_config_set([f"hostname {hostname}"])
    # Update netmiko's internal prompt to match the new hostname so it doesn't
    # time out waiting for a prompt that no longer exists.
    conn.set_base_prompt()

    # -- Base configuration --------------------------------------------------------
    # Applies domain name, local credentials, console/enable passwords, and
    # service password-encryption from the template file.
    output = conn.send_config_from_file("configs/base_config.txt")
    print(output)

    # -- VLAN creation -------------------------------------------------------------
    vlan_count = int(input("How many VLANs do you want to create? "))
    for i in range(vlan_count):
        confirm = input(f"Create VLAN {i + 1}? (y/n): ").strip().lower()
        if confirm != "y":
            continue

        vlan_id = input(f"  VLAN ID: ").strip()
        vlan_name = input(f"  VLAN name: ").strip()
        description = input(f"  Description: ").strip()

        conn.send_config_set([
            f"vlan {vlan_id}",
            f"name {vlan_name}",
            f"interface vlan {vlan_id}",
            f"description {description}",
        ])
        print(f"  VLAN {vlan_id} ({vlan_name}) created.")

    # -- Save configuration --------------------------------------------------------
    conn.save_config()
    print("Configuration saved successfully.")
