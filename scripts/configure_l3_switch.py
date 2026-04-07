"""
configure_l3_switch.py
----------------------
Automates full configuration for a Cisco Layer 3 switch.

Layer 3 switches can route traffic between VLANs using Switched Virtual
Interfaces (SVIs) — virtual Layer 3 interfaces assigned to each VLAN.
This eliminates the need for a separate router for inter-VLAN routing.

What this script does (in order):
  1. Asks how you want to connect (physical serial or telnet) via connection_handler
  2. Enters privileged exec mode (enable)
  3. Prompts for a hostname and sets it on the device
  4. Prompts for an IP domain name and configures it (required for SSH key gen)
  5. Enables 'ip routing' globally — activates Layer 3 packet forwarding
  6. Interactively creates VLANs with optional SVI configuration per VLAN
     (user provides VLAN ID, name, IP address, subnet mask, description)
  7. Optionally configures a static default route to an upstream gateway
  8. Saves the running configuration to NVRAM

Usage:
    python scripts/configure_l3_switch.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from connection_handler import get_connection

with get_connection() as conn:

    # Enter privileged exec mode so we can make configuration changes.
    conn.enable()

    # -- Hostname ----------------------------------------------------------------
    hostname = input("Hostname for this device: ").strip()
    conn.send_config_set([f"hostname {hostname}"])

    # After changing the hostname the CLI prompt changes (e.g. Switch# → Core01#).
    # set_base_prompt() reads the new prompt so netmiko doesn't time out.
    conn.set_base_prompt()

    # -- IP domain name ----------------------------------------------------------
    # Required for SSH RSA key generation (crypto key generate rsa).
    domain_name = input("IP domain name (e.g. example.com): ").strip()
    conn.send_config_set([f"ip domain-name {domain_name}"])

    # -- IP routing --------------------------------------------------------------
    # Globally enables Layer 3 packet forwarding between VLANs.
    # Without this, the switch behaves like a pure Layer 2 device even if
    # SVIs are configured with IP addresses.
    conn.send_config_set(["ip routing"])
    print("IP routing enabled.")

    # -- VLAN creation and SVI configuration ------------------------------------
    vlan_count = int(input("How many VLANs do you want to create? "))
    for i in range(vlan_count):
        confirm = input(f"Create VLAN {i + 1}? (y/n): ").strip().lower()
        if confirm != "y":
            continue

        vlan_id   = input("  VLAN ID: ").strip()
        vlan_name = input("  VLAN name: ").strip()

        # Create the VLAN and assign a name in the VLAN database.
        conn.send_config_set([f"vlan {vlan_id}", f"name {vlan_name}"])

        # SVI (Switched Virtual Interface): a virtual Layer 3 interface for
        # this VLAN. Assigning an IP makes the switch the default gateway for
        # all hosts in this VLAN and enables routing to other VLANs.
        svi_confirm = input(f"  Configure SVI (IP address) for VLAN {vlan_id}? (y/n): ").strip().lower()
        if svi_confirm == "y":
            ip_address  = input("  IP address (e.g. 192.168.10.1): ").strip()
            subnet_mask = input("  Subnet mask (e.g. 255.255.255.0): ").strip()
            description = input("  Description: ").strip()

            conn.send_config_set([
                f"interface vlan {vlan_id}",
                f"description {description}",
                f"ip address {ip_address} {subnet_mask}",
                "no shutdown",   # bring the SVI up; VLAN interfaces default to down
            ])
            print(f"  SVI for VLAN {vlan_id} configured: {ip_address} {subnet_mask}")

    # -- Static default route (optional) ----------------------------------------
    # A default route sends all traffic with no more-specific match to a
    # next-hop IP (typically the upstream router or firewall).
    route_confirm = input("Configure a static default route? (y/n): ").strip().lower()
    if route_confirm == "y":
        next_hop = input("  Next-hop IP address: ").strip()
        conn.send_config_set([f"ip route 0.0.0.0 0.0.0.0 {next_hop}"])
        print(f"  Default route via {next_hop} configured.")

    # -- Save configuration ------------------------------------------------------
    # Writes the running config to startup config (NVRAM) so it survives reboot.
    conn.save_config()
    print("Configuration saved successfully.")
