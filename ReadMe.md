# Network Config Automation
A collection of Python scripts using the netmiko library to automate pushing configs to network devices via Serial/Console Connection.
---------

# Requirements 
- Python 3.x 
- Mac with USB-to-Serial console cable 
- Network device with console port 
---

# Installation
1. Clone the repo 
git clone <repo-url>
cd NetworkAutomation

2. Create the virtual environment
python -m venv netautovenv
source netautovenv/bin/activate 

3. Install dependencies 
pip install -r requirements.txt 
-----

# Connection Information 
1. Check for terminal and serial devices connected to your device 
ls /dev/tty.*
- It will return multiple terminal and serial connection
- If using the usb to serial check for tty.usbserial-XXXX - "XXXX" unique number assigned by the macOS 
- Output will be more like dev/tty.usbserial-1420 
- This value is used in the script to establish connection between script and device via console connection

---

# Scripts

## Switch.py
Basic switch configuration script. Connects via console and:
- Sets the device hostname (user prompt)
- Applies base config from `switch.txt` (domain name, local user, console/enable passwords, service password-encryption)
- Creates VLANs interactively (user provides VLAN ID, name, and description)
- Saves the configuration

## l3switch.py
**Layer 3 switch** configuration script. Extends Switch.py with full L3 capabilities:
- Sets hostname and IP domain name (user prompt)
- Enables `ip routing` for inter-VLAN routing
- Creates VLANs interactively (user provides VLAN ID and name)
- Configures an SVI (Switched Virtual Interface) per VLAN with an IP address so the switch can route between VLANs
- Optionally configures a static default route (user provides next-hop IP)
- Saves the configuration

Usage:
```
python l3switch.py
```

## checkserialport.py
Helper script that lists all serial/TTY ports currently available on the system.
Use this to find the correct port name to put in the `device` dictionary inside `Switch.py` or `l3switch.py`.

Usage:
```
python checkserialport.py
```

