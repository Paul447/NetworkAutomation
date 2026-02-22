# Network Config Automationn 
A Python script using the netmiko library to automate pushing configs to network via Serial/Console Connection.
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
python -n venv netautovenv
source venv/bin/activate 

3. Install dependencies 
pip install -r requirements.txt 
-----

# Connection Information 
1. Check for terminal and serial devices connected to your device 
ls /dev/tty.*
- It will return multiple terminal and serial connection
- If using the usb to serial check for tty.usbserial-XXXX - "XXX" unique number assigned by the macOS 
- Output will be more like dev/tty.usbserial-1420 
- This value is used in the script to establish connection between script and device via console connection

