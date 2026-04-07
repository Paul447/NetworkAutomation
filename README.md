# Network Automation

> Automate Cisco switch configuration via serial/console using Python and [netmiko](https://github.com/ktbyers/netmiko).

Instead of manually typing commands into each device over a console cable, these scripts connect to the switch and push configuration automatically — setting hostnames, creating VLANs, configuring SVIs, enabling port security, and more.

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Connection Setup](#connection-setup)
- [Scripts](#scripts)
  - [find_serial_ports.py](#find_serial_portspy)
  - [configure_l2_switch.py](#configure_l2_switchpy)
  - [configure_l3_switch.py](#configure_l3_switchpy)
  - [configure_port_security.py](#configure_port_securitypy)
- [Configuration Template](#configuration-template)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

---

## Requirements

| Requirement | Details |
|---|---|
| Python | 3.8 or higher |
| OS | macOS (Linux also supported — see [Connection Setup](#connection-setup)) |
| Hardware | USB-to-serial console cable (e.g. USB-A to RJ45) |
| Device | Cisco IOS switch with a console port |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Paul447/NetworkAutomation.git
cd NetworkAutomation

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Project Structure

```
NetworkAutomation/
│
├── configs/
│   └── base_config.txt              # Base config template pushed to every switch
│                                    # (domain name, credentials, passwords, encryption)
│
├── scripts/
│   ├── find_serial_ports.py         # Step 1 — discover your console port
│   ├── configure_l2_switch.py       # Step 2a — configure a Layer 2 switch
│   ├── configure_l3_switch.py       # Step 2b — configure a Layer 3 switch
│   └── configure_port_security.py   # Step 3 — lock down switchport interfaces
│
├── requirements.txt                 # Python dependencies
└── README.md
```

---

## Connection Setup

### Step 1 — Find your serial port

Connect your USB-to-serial console cable to the switch, then run:

```bash
python scripts/find_serial_ports.py
```

**Example output (macOS):**
```
Available serial ports:
  /dev/tty.usbserial-1130
  /dev/tty.Bluetooth-Incoming-Port
```

Look for the entry containing `usbserial`. The number at the end (e.g. `1130`) is unique to your adapter.

> **Linux users:** Your port will appear as `/dev/ttyUSB0` or `/dev/ttyS0` instead.

### Step 2 — Update the port in your script

Open whichever script you plan to run and update the `port` value in the `device` dictionary:

```python
device = {
    "device_type": "cisco_ios_serial",
    "serial_settings": {
        "port": "/dev/tty.usbserial-1130",   # <-- replace with your port
        "baudrate": 9600,
    },
}
```

> The default baud rate for Cisco console connections is **9600**. Only change this if your device documentation specifies a different value.

### Step 3 — Enable credentials (if required)

If your switch has a username/password or enable secret configured, uncomment and fill in:

```python
device = {
    ...
    "username": "admin",
    "password": "YourPassword",
    "secret":   "YourEnableSecret",
}
```

---

## Scripts

### `find_serial_ports.py`

Lists all serial/TTY ports currently detected on the system. **Always run this first** to find the correct port name before running any configuration script.

```bash
python scripts/find_serial_ports.py
```

---

### `configure_l2_switch.py`

Performs base configuration for a **Layer 2 switch**. Connects to the device over console and interactively:

1. Sets the device hostname
2. Applies `configs/base_config.txt` — domain name, local credentials, console password, enable secret, and `service password-encryption`
3. Creates VLANs (you provide VLAN ID, name, and description for each)
4. Saves the running configuration to NVRAM

```bash
python scripts/configure_l2_switch.py
```

**Example session:**
```
Hostname for this device: CoreSwitch01
How many VLANs do you want to create? 2

Create VLAN 1? (y/n): y
  VLAN ID: 10
  VLAN name: MANAGEMENT
  Description: Management VLAN
  VLAN 10 (MANAGEMENT) created.

Create VLAN 2? (y/n): y
  VLAN ID: 20
  VLAN name: USERS
  Description: User access VLAN
  VLAN 20 (USERS) created.

Configuration saved successfully.
```

---

### `configure_l3_switch.py`

Performs full configuration for a **Layer 3 switch**, enabling inter-VLAN routing via Switched Virtual Interfaces (SVIs). Interactively:

1. Sets hostname and IP domain name
2. Enables `ip routing` globally (required for inter-VLAN routing)
3. Creates VLANs with optional SVI (IP address + subnet mask per VLAN interface)
4. Optionally configures a static default route to an upstream gateway
5. Saves the configuration

```bash
python scripts/configure_l3_switch.py
```

**Example session:**
```
Hostname for this device: DistroSwitch01
IP domain name (e.g. example.com): corp.local
IP routing enabled.

How many VLANs do you want to create? 1

Create VLAN 1? (y/n): y
  VLAN ID: 10
  VLAN name: MANAGEMENT
  Configure SVI (IP address) for VLAN 10? (y/n): y
  IP address (e.g. 192.168.10.1): 192.168.10.1
  Subnet mask (e.g. 255.255.255.0): 255.255.255.0
  Description: Management SVI
  SVI for VLAN 10 configured: 192.168.10.1 255.255.255.0

Configure a static default route? (y/n): y
  Next-hop IP address: 192.168.1.1
  Default route via 192.168.1.1 configured.

Configuration saved successfully.
```

**What is an SVI?**
A Switched Virtual Interface is a virtual Layer 3 interface assigned to a VLAN. Giving it an IP address lets the switch act as the default gateway for that VLAN and route traffic between VLANs without a separate router.

---

### `configure_port_security.py`

Configures **port security** on one or more switchport interfaces to restrict which devices can connect based on MAC address.

```bash
python scripts/configure_port_security.py
```

**What it configures per interface:**

| Setting | Description |
|---|---|
| `switchport mode access` | Sets port to access mode (required for port security) |
| `switchport port-security` | Enables port security on the interface |
| `maximum <n>` | Max MAC addresses allowed (default: 1) |
| `mac-address sticky` | Switch auto-learns and saves connected MACs |
| `violation <mode>` | Action taken when an unauthorized MAC is detected |
| `mac-address <MAC>` | Optional: pin a specific trusted MAC address |

**Violation modes:**

| Mode | What Happens | Port Stays Up? | Log Entry? |
|---|---|---|---|
| `shutdown` | Port is disabled immediately | No | Yes |
| `restrict` | Unauthorized frames dropped | Yes | Yes |
| `protect` | Unauthorized frames dropped silently | Yes | No |

> **Recommendation:** Use `shutdown` for high-security ports (default). Use `restrict` when you need the port to stay up while still logging violations.

**Example session:**
```
Enter interface(s) to secure, comma-separated (e.g. fa0/1, fa0/2, gi0/1): fa0/1, fa0/2

--- Configuring port security on fa0/1 ---
  Max allowed MAC addresses (default 1): 1
  Violation modes: shutdown | restrict | protect
  Violation mode (default: shutdown): shutdown
  Pin a specific trusted MAC address? (leave blank to skip):
  Port security applied to fa0/1: max=1, violation=shutdown, sticky=enabled.

--- Configuring port security on fa0/2 ---
  Max allowed MAC addresses (default 1): 2
  Violation modes: shutdown | restrict | protect
  Violation mode (default: shutdown): restrict
  Pin a specific trusted MAC address? (leave blank to skip): AA:BB:CC:DD:EE:FF
  Pinning MAC AA:BB:CC:DD:EE:FF to fa0/2.
  Port security applied to fa0/2: max=2, violation=restrict, sticky=enabled.

Port security configuration saved successfully.
```

---

## Configuration Template

**`configs/base_config.txt`** contains IOS commands applied line-by-line to the device. It is sent automatically by `configure_l2_switch.py`.

**Default contents:**
```
ip domain-name jackmid.lib.edu
username admin secret ABcd1234!
line console 0
password ABcd1234!
login
exit
enable secret ABcd1234!
service password-encryption
```

**Edit before running** to match your environment:

| Line | What to change |
|---|---|
| `ip domain-name` | Your organization's domain name |
| `username admin secret` | Local admin username and password |
| `line console 0 / password` | Console line password |
| `enable secret` | Privileged exec mode (enable) password |

> `service password-encryption` encrypts all plaintext passwords in the running config. Keep this enabled at all times.

---

## Troubleshooting

**`No serial ports found`**
- Verify the USB-to-serial cable is physically connected
- Unplug and re-plug the cable and re-run the script
- On macOS, you may need a driver for your adapter chip (CH340 or CP2102 are common — search for the chip name + "macOS driver")

**netmiko hangs or times out on connect**
- Confirm the port name is correct by running `find_serial_ports.py`
- Baud rate must be `9600` (Cisco default)
- The cable must be in the **console** port — not AUX or USB management
- Press **Enter** on the device before running the script to wake the console session

**`Invalid input detected` error on device**
- The switch may be in ROMMON or setup mode — boot it fully first
- Confirm `enable` is accessible (correct `secret` in the `device` dict)
- Check the IOS version supports the commands being sent

**`Permission denied` on serial port (Linux)**

```bash
sudo usermod -aG dialout $USER
# Log out and back in for the change to take effect
```

---

## Roadmap

| Feature | Description |
|---|---|
| **SSH hardening** | Generate RSA keys, restrict VTY lines to SSH-only (`transport input ssh`) |
| **Config backup & restore** | Save `show running-config` to a timestamped file; push it back on demand |
| **DHCP pool setup** | Wizard for creating DHCP scopes on L3 switches |
| **Trunk & EtherChannel** | Automate 802.1Q trunk links and LACP port channels |
| **OSPF / EIGRP** | Basic dynamic routing setup wizard |
| **Linux / Windows support** | Auto-detect OS, use `/dev/ttyUSB*` or `COM*` serial patterns |
| **Dry-run / validation mode** | Print commands to console without sending to the device |
