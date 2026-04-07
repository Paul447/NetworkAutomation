"""
Layer 3 Switch Configuration Script

Automates L3 switch setup via a serial/console connection:
  - Sets hostname and IP domain name
  - Enables IP routing for inter-VLAN routing
  - Creates VLANs interactively (user provides VLAN ID and name)
  - Optionally configures a Switched Virtual Interface (SVI) per VLAN
    with an IP address and subnet mask
  - Optionally configures a static default route
  - Saves the running configuration

Requirements:
  - USB-to-serial console cable connected to the switch
  - Run scripts/find_serial_ports.py to find the correct port (e.g. /dev/tty.usbserial-1130)
  - Update the 'port' value in the device dictionary below before running

Usage:
    python scripts/configure_l3_switch.py
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
    # Update netmiko's internal prompt to match the new hostname.
    conn.set_base_prompt()

    # -- Domain name ---------------------------------------------------------------
    domain_name = input("IP domain name (e.g. example.com): ").strip()
    conn.send_config_set([f"ip domain-name {domain_name}"])

    # -- IP routing ----------------------------------------------------------------
    # Required for inter-VLAN routing on an L3 switch.
    conn.send_config_set(["ip routing"])
    print("IP routing enabled.")

    # -- VLAN creation and SVI configuration ---------------------------------------
    vlan_count = int(input("How many VLANs do you want to create? "))
    for i in range(vlan_count):
        confirm = input(f"Create VLAN {i + 1}? (y/n): ").strip().lower()
        if confirm != "y":
            continue

        vlan_id = input(f"  VLAN ID: ").strip()
        vlan_name = input(f"  VLAN name: ").strip()
        conn.send_config_set([f"vlan {vlan_id}", f"name {vlan_name}"])

        # SVI: assign an IP to the VLAN interface so the switch can route
        # traffic between VLANs.
        svi_confirm = input(f"  Configure SVI (IP address) for VLAN {vlan_id}? (y/n): ").strip().lower()
        if svi_confirm == "y":
            ip_address = input(f"  IP address (e.g. 192.168.10.1): ").strip()
            subnet_mask = input(f"  Subnet mask (e.g. 255.255.255.0): ").strip()
            description = input(f"  Description: ").strip()
            conn.send_config_set([
                f"interface vlan {vlan_id}",
                f"description {description}",
                f"ip address {ip_address} {subnet_mask}",
                "no shutdown",
            ])
            print(f"  SVI for VLAN {vlan_id} configured: {ip_address} {subnet_mask}")

    # -- Static default route (optional) ------------------------------------------
    route_confirm = input("Configure a static default route? (y/n): ").strip().lower()
    if route_confirm == "y":
        next_hop = input("  Next-hop IP address: ").strip()
        conn.send_config_set([f"ip route 0.0.0.0 0.0.0.0 {next_hop}"])
        print(f"  Default route via {next_hop} configured.")

    # -- Save configuration --------------------------------------------------------
    conn.save_config()
    print("Configuration saved successfully.")
