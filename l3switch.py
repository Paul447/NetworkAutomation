from netmiko import ConnectHandler


"""
- This script is used to automate basic configuration of an L3 (Layer 3) switch via console.
- L3 switches support IP routing between VLANs using Switched Virtual Interfaces (SVIs).
- User is prompted for all customizable settings (hostname, domain, VLANs, SVIs, static route).
- Connection handler function from netmiko is used to establish a connection to the device.
"""

# Define the device parameters in dictionary format
device = {
    # This line tells netmiko that we are using a Cisco device connecting via console.
    "device_type": "cisco_ios_serial",
    "serial_settings": {
        # Check Readme file # Connection Information
        "port": "/dev/cu.usbserial-1130",  # Run checkserialport.py to find your port (e.g. /dev/tty.usbserial-XXXX)
        "baudrate": 9600,  # Default baud rate for most Cisco devices.
    },
    # "username": "admin", # Uncomment if device requires username/password
    # "password": "ABcd1234!",
    # "secret": "ABcd1234!"  # Enable/privileged exec mode password
}

with ConnectHandler(**device) as conn:
    conn.enable()  # Enter privileged exec mode

    # ── Hostname ──────────────────────────────────────────────────────────────
    device_name = input("Please specify the Hostname of the Device: ")
    conn.send_config_set([f"hostname {device_name}"])
    # Update netmiko's internal prompt so it matches the new hostname.
    conn.set_base_prompt()

    # ── Domain name ───────────────────────────────────────────────────────────
    domain_name = input("Please specify the IP Domain Name (e.g. example.com): ")
    conn.send_config_set([f"ip domain-name {domain_name}"])

    # ── Enable IP routing (required for L3 switching / inter-VLAN routing) ───
    conn.send_config_set(["ip routing"])
    print("IP routing enabled.")

    # ── VLAN creation and SVI configuration ──────────────────────────────────
    vlan_count = int(input("How many VLANs do you want to create? "))
    for i in range(vlan_count):
        confirm = input(f"Do you want to create VLAN {i + 1}? (y/n): ")
        if confirm.strip().lower() != 'y':
            continue

        vlan_id = input(f"  Enter the VLAN ID for VLAN {i + 1}: ").strip()
        vlan_name = input(f"  Enter the VLAN Name for VLAN {i + 1}: ").strip()

        # Create the VLAN and assign a name.
        conn.send_config_set([f"vlan {vlan_id}", f"name {vlan_name}"])

        # SVI: assign an IP address to the VLAN interface so the switch can
        # route traffic to/from that VLAN.
        svi_confirm = input(f"  Configure an SVI (IP address) for VLAN {vlan_id}? (y/n): ")
        if svi_confirm.strip().lower() == 'y':
            ip_address = input(f"  Enter the IP address for VLAN {vlan_id} SVI (e.g. 192.168.10.1): ").strip()
            subnet_mask = input(f"  Enter the subnet mask (e.g. 255.255.255.0): ").strip()
            description = input(f"  Enter the description for VLAN {vlan_id} SVI: ").strip()
            conn.send_config_set([
                f"interface vlan {vlan_id}",
                f"description {description}",
                f"ip address {ip_address} {subnet_mask}",
                "no shutdown",
            ])
            print(f"  SVI for VLAN {vlan_id} configured with IP {ip_address} {subnet_mask}.")

    # ── Optional static default route ─────────────────────────────────────────
    route_confirm = input("Do you want to configure a static default route? (y/n): ")
    if route_confirm.strip().lower() == 'y':
        next_hop = input("  Enter the next-hop IP address for the default route: ").strip()
        conn.send_config_set([f"ip route 0.0.0.0 0.0.0.0 {next_hop}"])
        print(f"  Default route via {next_hop} configured.")

    # ── Save configuration ────────────────────────────────────────────────────
    conn.save_config()
    print("Configuration saved successfully.")
