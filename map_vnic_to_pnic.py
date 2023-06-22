"""
Script to connect to an ESXi host over SSH and map vnic to vmnic in a new file
Author: Daryl Allen
"""

import argparse
import json
import socket
from concurrent.futures import ThreadPoolExecutor # I'm leaving this in place for a future code version
from paramiko import SSHClient, AutoAddPolicy
import sys

# Credentials file example:
# {"username": "your_username", "password": "your_password"}

# Function to parse VM process list from the output of an SSH command
def parse_vm_process_list(output):
    vms = []
    current_vm = {}

    for line in output:
        if line.strip() == "":
            if current_vm:
                vms.append(current_vm)
                current_vm = {}
        elif ":" in line:
            key, value = line.split(":", 1)
            current_vm[key.strip()] = value.strip()

    if current_vm:
        vms.append(current_vm)

    return vms

# Function to parse network statistics from the output of an SSH command
def parse_net_stats(output):
    stats = []

    for line in output:
        if line.strip() == "":
            continue

        parts = line.split()
        if len(parts) != 6:
            print(f"Unexpected format: {line}")
            continue

        stat = {
            "Port ID": parts[0],
            "Type": parts[1],
            "SubType": parts[2],
            "Switch Name": parts[3],
            "MAC Address": parts[4],
            "VM Name": parts[5]
        }
        stats.append(stat)

    return stats


# Load SSH credentials from a JSON file
def load_credentials(file_name="credentials.json"):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"The file {file_name} does not exist.")
        sys.exit(1)


# Check if a port is open on a host
def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    return result == 0


# Connect to a host over SSH and execute a command
def send_command(host, credentials, cli_command):
    if not check_port(host, 22):
        print(f"The ESXi host {host} is not listening on port 22.")
        return []

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())

    try:
        with ssh:
            ssh.connect(host, username=credentials["username"], password=credentials["password"])
            stdin, stdout, stderr = ssh.exec_command(cli_command)
            output = stdout.readlines()
            return output
    except socket.timeout:
        print(f"Socket timeout when trying to connect to {host}.")
    except Exception as e:
        print(
            f"Unable to connect to {host} with provided credentials. The host may have non-standard credentials. Error: {e}")
    return []


# Main function
def main():
    # Define command-line arguments for the script
    parser = argparse.ArgumentParser(
        description="This script connects to an ESXi host over SSH and maps vm vnic to pnic")
    # Argument for the file that contains the list of hosts
    parser.add_argument("inventory_file", help="File containing the list of hosts.")
    # Argument for the file that contains SSH credentials. Defaults to 'credentials.json' if not provided
    parser.add_argument("-f", "--credentials_file", default="credentials.json",
                        help="File containing the SSH credentials. Defaults to 'credentials.json'.")
    args = parser.parse_args()

    # Initialize variables with the provided arguments
    inventory_file = args.inventory_file
    credentials_file = args.credentials_file

    # Load hosts from inventory file
    try:
        # Open the inventory file and read the list of hosts
        with open(inventory_file, "r") as file:
            hosts = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        # Exit the script if the inventory file does not exist
        print(f"The file {inventory_file} does not exist.")
        sys.exit(1)

    # Initialize an empty dictionary to store the final data
    data = {}

    # Load SSH credentials
    credentials = load_credentials(credentials_file)

    # Loop over the list of hosts
    for host in hosts:
        # Send an SSH command to get the VM process list and parse the output
        process_list = send_command(host, credentials, "esxcli vm process list")
        vm_process_list = parse_vm_process_list(process_list)

        # For each VM in the process list, get the pNIC info and parse it
        for vm in vm_process_list:
            vm_pnic_info = send_command(host, credentials, f"esxcli network vm port list -w {vm['World ID']}")
            vm_pnic_info_processed = parse_vm_process_list(vm_pnic_info)

            # Print the VM name and world ID
            print(f"VM Name: {vm['Display Name']}, World ID: {vm['World ID']}")

            # Get the port ID(s) associated with the VM and parse them
            vm_port_ids = send_command(host, credentials, f"net-stats -l | grep {vm['Display Name']}")
            vm_port_ids_processed = parse_net_stats(vm_port_ids)

            # For each piece of pNIC info, create a dictionary and append it to the data dictionary under the VM name
            for info in vm_pnic_info_processed:
                vm_name = vm['Display Name']
                mac_address = info['MAC Address']
                vmnic = info['Team Uplink']
                portgroup = info['Portgroup']
                port_id = info['Port ID']

                # If the VM name is not already a key in the data dictionary, add it
                if vm_name not in data:
                    data[vm_name] = []

                # Append the pNIC info dictionary to the list associated with the VM name in the data dictionary
                data[vm_name].append({
                    "MAC Address": mac_address,
                    "vmnic": vmnic,
                    "Portgroup": portgroup,
                    "Port ID": port_id
                })

    # Write the data dictionary to a JSON file
    with open('output.json', 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()


