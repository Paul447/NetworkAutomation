# Contributing to Network Automation

Thanks for your interest in contributing! This project is a practical toolkit for automating Cisco switch configuration. Contributions that add new scripts, improve reliability, or extend platform support are welcome.

---

## Getting Started

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/NetworkAutomation.git
cd NetworkAutomation

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Project Structure

```
NetworkAutomation/
├── configs/          # IOS config templates (plain-text command files)
├── scripts/          # Automation scripts — one script per feature/task
├── requirements.txt
├── README.md
└── CONTRIBUTING.md
```

---

## Adding a New Script

Each script in `scripts/` follows a consistent pattern:

1. **Module docstring at the top** — explain what the script does, what it configures, requirements, and usage
2. **`device` dictionary** — connection parameters with `port` marked `# <-- update this`
3. **Section comments** (`# -- Section name ---`) to visually separate logical steps
4. **Inline comments** for any non-obvious IOS behaviour (e.g. why `set_base_prompt()` is needed after a hostname change)
5. **`conn.save_config()`** at the end — always save

### Template

```python
"""
your_script_name.py
-------------------
One-line summary of what this script automates.

What this script does (in order):
  1. ...
  2. ...

Before running:
  - Run scripts/find_serial_ports.py to find your port
  - Update 'port' in the device dictionary below
  - ...

Usage:
    python scripts/your_script_name.py
"""

from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_serial",
    "serial_settings": {
        "port": "/dev/tty.usbserial-1130",  # <-- update this
        "baudrate": 9600,
    },
    # "username": "admin",
    # "password": "ABcd1234!",
    # "secret":   "ABcd1234!",
}

with ConnectHandler(**device) as conn:
    conn.enable()

    # -- Your section here -------------------------------------------------------
    ...

    conn.save_config()
    print("Configuration saved successfully.")
```

---

## Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Script files | `snake_case`, verb-prefixed | `configure_l2_switch.py` |
| Config templates | `snake_case` | `base_config.txt` |
| Variables | `snake_case` | `vlan_id`, `next_hop` |
| Functions | `snake_case`, descriptive | `configure_port_security_on_interface()` |

---

## Commit Messages

Use the imperative mood and be specific:

```
# Good
Add configure_ssh_hardening.py for VTY SSH-only access
Fix port serial pattern for Linux (/dev/ttyUSB*)
Update README with Linux serial port troubleshooting

# Avoid
fixed stuff
update
wip
```

---

## Pull Request Checklist

Before opening a PR:

- [ ] Script has a full module docstring (purpose, steps, requirements, usage)
- [ ] Section comments are present for each logical block
- [ ] Non-obvious IOS behaviour is explained inline
- [ ] `conn.save_config()` is called at the end
- [ ] `port` in the `device` dict is marked `# <-- update this`
- [ ] README.md is updated if a new script was added
- [ ] Tested on a real device or Packet Tracer / GNS3

---

## Ideas for New Scripts

See the [Roadmap section in README.md](README.md#roadmap) for a list of planned features. If you'd like to work on one, open an issue first to avoid duplicate effort.
