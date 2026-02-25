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
        "port": "/dev/cu.usbserial-1130", 
        "baudrate": 9600, # At what speed the connection will be established. For most devices, the default baud rate is 9600. If different check in device information.
    },
    # "username": "admin", # If device require username and password this is the thing used 
    # "password": "ABcd1234!", # If device require line console password 
    # "secret": "ABcd1234!" # If device require previliged exec mode password
}

with ConnectHandler(**device) as conn:
    conn.enable() # This line is used to enter into the privileged exec mode
    # output = conn.send_command("show run") # This line is used to send the command to the device and store the output in a variable
    # print(output) # This line is used to print the output of the command
    device_name = input("Please specify the Host Name of the Device : ")
    # This is used to set the hostname and parameter enter_config_mode and exit_config_mode is used to enter and exit the configuration mode after sending the command.
    conn.send_config_set([f"hostname {device_name}"]) # This line is used to change the hostname of the device
    # set_base_prompt that reads the current CLI prompt from the device store it internally.
    # So that netmiko knows what to expect at the end of the command output 
    # For example if the oldname is "Switch" and new name is "NewSwitch" then the prompt will change from "Switch>" to "NewSwitch>" and if we don't set the base prompt then netmiko will expect the old prompt and it will not be able to find the new prompt and it will throw an error.
    conn.set_base_prompt()
    output = conn.send_config_from_file("switch.txt") # This line is used to send the commands from the text file to the device and store the output in a variable
    print(output) # This line is used to print the output of the commands from the text

    # Check for the how many VLANs needed and ask for the user input and then create the VLANs on the device.
    vlan_count = int(input("How many VLANs do you want to create? "))
    for i in range(vlan_count):
        confirm = input(f"Do you want to create VLAN {i + 1}? (y/n) : ")
        if confirm.lower() != 'y':
            continue
        vlan_id = input(f"Enter the VLAN ID for VLAN {i+1}: ")
        vlan_name = input(f"Enter the VLAN Name for VLAN {i+1}: ")
        description = input(f"Enter the description for VLAN {i+1}: ")
        conn.send_config_set([f"vlan {vlan_id}", f"name {vlan_name}", f"interface vlan {vlan_id}", f"description {description}"], enter_config_mode=True, exit_config_mode=True) # This line is used to create the VLANs on the device
    
    conn.save_config() # This line is used to save the configuration on the device