# Network Automation

A collection of Python scripts using the [netmiko](https://github.com/ktbyers/netmiko) library to automate pushing configurations to Cisco network devices via a serial/console connection.

---

## Requirements

- Python 3.x
- macOS with a USB-to-serial console cable
- Cisco switch with a console port

---

## Installation

```bash
# 1. Clone the repo
git clone <repo-url>
cd NetworkAutomation

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Project Structure

```
NetworkAutomation/
├── configs/
│   └── base_config.txt              # Base config template (credentials, domain, passwords)
├── scripts/
│   ├── configure_l2_switch.py       # Layer 2 switch setup
│   ├── configure_l3_switch.py       # Layer 3 switch setup (inter-VLAN routing)
│   ├── configure_port_security.py   # Port security on switchport interfaces
│   └── find_serial_ports.py         # Utility: discover available serial ports
├── requirements.txt
└── README.md
```

---

## Connection Setup

1. Connect your USB-to-serial cable to the switch console port.
2. Run the helper script to find your port:
   ```bash
   python scripts/find_serial_ports.py
   ```
   Look for an entry like `/dev/tty.usbserial-XXXX`.
3. Open the target script and update the `port` value in the `device` dictionary:
   ```python
   "port": "/dev/tty.usbserial-1130",  # <-- change this
   ```

---

## Scripts

### `scripts/configure_l2_switch.py`
Basic Layer 2 switch configuration. Interactively:
- Sets the device hostname
- Applies the base config template (`configs/base_config.txt`)
- Creates VLANs (ID, name, description)
- Saves the configuration

```bash
python scripts/configure_l2_switch.py
```

---

### `scripts/configure_l3_switch.py`
Layer 3 switch configuration with full inter-VLAN routing support. Interactively:
- Sets hostname and IP domain name
- Enables `ip routing`
- Creates VLANs (ID, name)
- Configures Switched Virtual Interfaces (SVIs) with IP addresses
- Optionally sets a static default route
- Saves the configuration

```bash
python scripts/configure_l3_switch.py
```

---

### `scripts/configure_port_security.py`
Port security configuration for one or more switchport interfaces. Interactively:
- Sets maximum allowed MAC addresses per port
- Enables sticky MAC learning
- Sets the violation mode (`shutdown` / `restrict` / `protect`)
- Optionally pins a specific trusted MAC address
- Saves the configuration

```bash
python scripts/configure_port_security.py
```

---

### `scripts/find_serial_ports.py`
Helper utility that lists all serial/TTY ports available on the system.
Run this first to identify the correct port for your USB-to-serial adapter.

```bash
python scripts/find_serial_ports.py
```

---

## Configuration Template

`configs/base_config.txt` is applied by `configure_l2_switch.py` during setup.
Edit this file to change the default domain name, credentials, or security settings before running the script.

---

## Ideas & Roadmap

See the **Ideas** section below for planned features and enhancements.

### Planned Features
- **DHCP pool configuration** — automate DHCP scope creation on L3 switches
- **SSH hardening script** — generate RSA keys, configure VTY lines for SSH-only access
- **Trunk & EtherChannel setup** — automate 802.1Q trunk links and LACP port channels
- **OSPF / EIGRP configuration** — basic dynamic routing setup wizard
- **Backup & restore** — pull `show running-config` to a timestamped local file and push it back
- **Linux/Windows support** — detect OS and adjust serial port patterns (`/dev/ttyUSB*` on Linux, `COM*` on Windows)
- **Config validation** — dry-run mode that prints commands without sending them
