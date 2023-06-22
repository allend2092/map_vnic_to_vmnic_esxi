"""
Script to connect to an ESXi host over SSH and map vnic to vmnic in a new file
Author: Daryl Allen
"""

import argparse
import json
import socket
from concurrent.futures import ThreadPoolExecutor
from paramiko import SSHClient, AutoAddPolicy
import sys

# Credentials file example:
# {"username": "your_username", "password": "your_password"}

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
    parser = argparse.ArgumentParser(
        description="This script connects to an ESXi host over SSH and maps vm vnic to pnic")
    parser.add_argument("inventory_file", help="File containing the list of hosts.")
    parser.add_argument("-f", "--credentials_file", default="credentials.json",
                        help="File containing the SSH credentials. Defaults to 'credentials.json'.")
    args = parser.parse_args()

    # initialize variables
    inventory_file = args.inventory_file
    credentials_file = args.credentials_file

    # Load hosts from inventory file
    try:
        with open(inventory_file, "r") as file:
            hosts = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"The file {inventory_file} does not exist.")
        sys.exit(1)

    credentials = load_credentials(credentials_file)
    for host in hosts:
        output = send_command(host, credentials, "esxcli vm process list")
        vms = parse_vm_process_list(output)
        for vm in vms:
            print(f"VM Name: {vm['Display Name']}, World ID: {vm['World ID']}")


if __name__ == "__main__":
    main()
