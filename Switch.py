from netmiko import ConnectHandler 


"""
- This script is used to connect to a switch via console .
- Execute a command from the text file.
- Connection handler function from netmiko is used to establish a connection to the device. 
"""

# Define the device parameters in dictionary format
device = {
    # This lines tells netmiko that we are using the cisco device and establishing a connection via console.
    "device_type": "cisco_ios_serial", 
    "serial_settings": {
        # Check Readme file # Connection Information
        "port": "/dev/tty.usbserial-XXXX", 
        "baudrate": 9600, # At what speed the connection will be established. For most devices, the default baud rate is 9600. If different check in device information.
    },
    "username": "admin", # If device require username and password this is the thing used 
    "password": "ABcd1234!", # If device require line console password 
    "secret": "ABcd1234!" # If device require previliged exec mode password
}

with ConnectHandler(**device) as conn:
    conn.enable() # This line is used to enter into the privileged exec mode
    output = conn.send_command("show version") # This line is used to send the command to the device and store the output in a variable
    print(output) # This line is used to print the output of the command
    output = conn.send_config_from_file("commands.txt") # This line is used to send the commands from the text file to the device and store the output in a variable
    print(output) # This line is used to print the output of the commands from the text
    conn.save_config() # This line is used to save the configuration on the device