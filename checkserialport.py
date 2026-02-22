import glob

def check_serial_port():
    ports = glob.glob("/dev/tty.*")
    print(ports)

check_serial_port()