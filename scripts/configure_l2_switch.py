"""
configure_l2_switch.py
----------------------
Automates base configuration for a Cisco Layer 2 switch.

What this script does (in order):
  1. Asks how you want to connect (physical serial or telnet) via connection_handler
  2. Enters privileged exec mode (enable)
  3. Prompts for a hostname and sets it on the device
  4. Applies configs/base_config.txt — sets domain name, local credentials,
     console password, enable secret, and service password-encryption
  5. Interactively creates VLANs (user provides VLAN ID, name, description)
  6. Saves the running configuration to NVRAM (write memory)

Before running:
  - Edit configs/base_config.txt to match your credentials and domain name

Usage:
    python scripts/configure_l2_switch.py
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
