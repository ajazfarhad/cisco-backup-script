from netmiko import ConnectHandler
from tqdm import tqdm
import configparser
import datetime
import os
from pathlib import Path

# Generate IP addresses in the range 10.2.11.1 to 10.2.11.100
def get_ip_addresses():
    ip_addresses = []
    for i in range(1, 101):
        ip_addresses.append(f"10.2.11.{i}")
    return ip_addresses

# Create a directory to store the backup configurations on the desktop
def create_backup_dir(timestamp):
    desktop_path = Path.home() / "Desktop"
    backup_dir = desktop_path / "switches_backup_data" / timestamp
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
    return backup_dir

# Read credentials and device type from the config file
def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config.get('cisco_switch', 'username')
    password = config.get('cisco_switch', 'password')
    device_type = config.get('cisco_switch', 'device_type')
    return username, password, device_type

# Copy the running configuration from the device
def copy_running_config(ip_address, timestamp, dir_path, username, password, device_type):
    try:
        print(f"Copying config of switch with IP {ip_address}")
        cisco_switch = {
            'device_type': device_type,
            'ip': ip_address,
            'username': username,
            'password': password,
        }

        filename = f"{ip_address}-{timestamp}.txt"
        filepath = dir_path / filename

        with ConnectHandler(**cisco_switch) as ssh_connect:
            ssh_connect.enable()
            response = ssh_connect.send_command('show running-config')
            with open(filepath, "w") as config_file:
                config_file.write(response)

        print(f"Done copying config for IP {ip_address}")
    except Exception as e:
        print(f"Error for switch with IP {ip_address}: {e}")

def main():
    # Get the current timestamp
    now = datetime.datetime.now()
    timestamp = now.strftime("%m-%d-%Y-%H-%M-%S")

    # Create a directory for backups on the desktop if it doesn't exist
    backup_dir = create_backup_dir(timestamp)

    # Get the list of IP addresses
    ip_addresses = get_ip_addresses()

    # Get the configuration details
    username, password, device_type = get_config()

    # Copy running config for each IP address with progress bar
    for ip_address in tqdm(ip_addresses, desc="Copying configurations", unit="switch"):
        copy_running_config(ip_address, timestamp, backup_dir, username, password, device_type)

if __name__ == "__main__":
    main()
