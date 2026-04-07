# configs/

This directory holds IOS configuration templates — plain-text files where each line is a Cisco IOS command. Scripts send these files line-by-line to the device using netmiko's `send_config_from_file()`.

---

## `base_config.txt`

Applied by `scripts/configure_l2_switch.py` during the initial setup of a Layer 2 switch.

### Contents

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

### What each line does

| Command | Purpose |
|---|---|
| `ip domain-name <domain>` | Sets the switch's DNS domain. Required for SSH RSA key generation. |
| `username admin secret <pass>` | Creates a local admin account with an encrypted password. Used for console/SSH login. |
| `line console 0` | Enters console line configuration mode. |
| `password <pass>` | Sets the console line password (asked before login prompt). |
| `login` | Enables password authentication on the console line. |
| `exit` | Returns to global config mode. |
| `enable secret <pass>` | Sets the privileged exec (enable) mode password. Uses MD5 encryption — stronger than `enable password`. |
| `service password-encryption` | Encrypts all plaintext passwords stored in `show running-config`. Prevents shoulder-surfing of config dumps. |

### Customising before use

Edit this file to match your environment before running any script:

- Replace `jackmid.lib.edu` with your organisation's domain name
- Replace `ABcd1234!` with strong, unique passwords
- Change `admin` to your preferred local username

### Adding more commands

You can extend this file with any valid IOS global config commands, for example:

```
# Disable unused services
no ip http server
no ip http secure-server
no cdp run

# Set timezone
clock timezone EST -5 0

# Set login banner
banner motd # Authorised access only #
```

---

## Adding new templates

To create a template for a new script:

1. Add a `.txt` file in this directory (e.g. `ssh_hardening.txt`)
2. Write one IOS config command per line
3. Reference it in your script with:
   ```python
   conn.send_config_from_file("configs/ssh_hardening.txt")
   ```
