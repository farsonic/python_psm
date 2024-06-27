import csv
import json
import requests
import sys
import urllib3
import argparse
import os
import ipaddress
import psm
from tabulate import tabulate

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize the argument parser
parser = argparse.ArgumentParser(description='Add a policy to PSM')
parser.add_argument('--name', type=str, help='Name of the policy')
#parser.add_argument('--policy-dist-target', type=str, help='Policy distribution targets')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
parser.add_argument('--load-json', type=str, help='Load policy from JSON file')
parser.add_argument('--save-json', type=str, help='Save policy to JSON file')
#parser.add_argument('--source-ip-addresses', type=str, help='Source IP addresses in CIDR notation (comma-separated)')
#parser.add_argument('--destination-ip-addresses', type=str, help='Destination IP addresses in CIDR notation (comma-separated)')
parser.add_argument('--import-csv', type=str, help='Import iterations from CSV file')

# Parse the command line arguments
args = parser.parse_args()

# Ensure either --name or --load-json is provided
if not args.name and not args.load_json:
    parser.error("the following arguments are required: --name or --load-json")

# Obtain the token
token = psm.ObtainPSMToken()

if args.debug:
    print("Token obtained successfully.")

# Function to post the policy to PSM
def post_policy_to_psm(token, policy_data):
    psmipaddress = json.load(open('config.json'))['psmipaddress']
    url = f"https://{psmipaddress}/configs/security/v1/tenant/default/networksecuritypolicies/{policy_data['meta']['name']}"
    headers = psm.constructHeader(token)
    response = requests.put(url, headers=headers, data=json.dumps(policy_data), verify=False)
    return response.status_code, response.json()

# Function to increment IP address within a subnet
def increment_ip(ip_str, increment):
    ip = ipaddress.IPv4Address(ip_str)
    return str(ip + increment)

# Check if a JSON file is provided to load the policy data
if args.load_json:
    with open(args.load_json, 'r') as file:
        policy_data = json.load(file)
    print(f"Loaded policy data from {args.load_json}")
else:
    # Initialize policy data structure
    policy_data = {
        "kind": None,
        "api-version": None,
        "meta": {
            "name": args.name,
            "tenant": "default",
            "namespace": None,
            "generation-id": None,
            "resource-version": None,
            "uuid": None,
            "labels": None,
            "self-link": None,
            "display-name": None
        },
        "spec": {
            "attach-tenant": True,
            "rules": [],
            "priority": 10,
            "policy-distribution-targets": [
                args.policy_dist_target if args.policy_dist_target else "default"
            ]
        }
    }

    # Check if a CSV file is provided to load the iteration data
    if args.import_csv and os.path.isfile(args.import_csv):
        with open(args.import_csv, 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            iterations_data = [row for row in csv_reader]
        print(f"Loaded iteration data from {args.import_csv}")
    else:
        # Ensure that --name is provided if not loading from CSV
        if not args.name:
            parser.error("the following arguments are required: --name when not using --import-csv")

        # Prompt for the number of iterations
        iterations = int(input("Enter the number of iterations: "))

        iterations_data = []
        for i in range(iterations):
            print(f"--- Iteration {i+1} ---")

            apps = input("Enter Apps (comma separated, default HTTP): ") or "HTTP"
            action = input("Enter Action (default permit): ") or "permit"
            from_ip_collections = input("Enter From IP Collection (default none): ") or ""
            to_ip_collections = input("Enter To IP Collection (default none): ") or ""
            from_workload_group = input("Enter From Workload Group (default none): ") or ""
            to_workload_group = input("Enter To Workload Group (default none): ") or ""

            if not from_ip_collections and not to_ip_collections and not from_workload_group and not to_workload_group:
                source_cidrs = input(f"Enter Source IP Subnets (comma-separated, default 10.{i+1}.0.0/16): ").split(',') or [f"10.{i+1}.0.0/16"]
                dest_cidrs = input(f"Enter Destination IP Subnets (comma-separated, default 10.{101+i}.0.0/16): ").split(',') or [f"10.{101+i}.0.0/16"]
                num_rules = int(input("Enter the number of rules to create: "))
            else:
                source_cidrs = []
                dest_cidrs = []
                num_rules = 1  # Default to 1 if using IP collections or workload groups

            iteration_data = {
                "apps": apps,
                "action": action,
                "from_ip_collections": from_ip_collections,
                "to_ip_collections": to_ip_collections,
                "from_workload_group": from_workload_group,
                "to_workload_group": to_workload_group,
                "source_cidrs": source_cidrs,
                "dest_cidrs": dest_cidrs,
                "num_rules": num_rules
            }
            iterations_data.append(iteration_data)

    total_rules = 0
    table_data = []
    for i, iteration_data in enumerate(iterations_data):
        if args.debug:
            print(f"--- Processing Iteration {i+1} ---")

        apps = iteration_data["apps"]
        action = iteration_data["action"]
        from_ip_collections = iteration_data["from_ip_collections"]
        to_ip_collections = iteration_data["to_ip_collections"]
        from_workload_group = iteration_data["from_workload_group"]
        to_workload_group = iteration_data["to_workload_group"]
        source_cidrs = iteration_data["source_cidrs"]
        dest_cidrs = iteration_data["dest_cidrs"]
        num_rules = iteration_data["num_rules"]

        if args.debug:
            print(f"Parsed values:\n  apps: {apps}\n  action: {action}\n  from_ip_collections: {from_ip_collections}\n  to_ip_collections: {to_ip_collections}\n  from_workload_group: {from_workload_group}\n  to_workload_group: {to_workload_group}\n  source_cidrs: {source_cidrs}\n  dest_cidrs: {dest_cidrs}\n  num_rules: {num_rules}")

        total_rules += int(num_rules)

        # Filter out any empty strings from the CIDR lists
        if isinstance(source_cidrs, list):
            source_cidrs = [cidr.strip() for cidr in source_cidrs if cidr.strip()]
        else:
            source_cidrs = [cidr.strip() for cidr in source_cidrs.split(',') if cidr.strip()]

        if isinstance(dest_cidrs, list):
            dest_cidrs = [cidr.strip() for cidr in dest_cidrs if cidr.strip()]
        else:
            dest_cidrs = [cidr.strip() for cidr in dest_cidrs.split(',') if cidr.strip()]

        # Use default if no valid subnets are provided
        if not source_cidrs and not from_ip_collections:
            source_cidrs = [f"10.{i+1}.0.0/16"]
        if not dest_cidrs and not to_ip_collections:
            dest_cidrs = [f"10.{101+i}.0.0/16"]

        if args.debug:
            print(f"Processed CIDRs:\n  source_cidrs: {source_cidrs}\n  dest_cidrs: {dest_cidrs}")

        # Convert the CIDRs to network objects
        try:
            if source_cidrs:
                source_networks = [ipaddress.ip_network(cidr, strict=False) for cidr in source_cidrs]
            else:
                source_networks = []

            if dest_cidrs:
                dest_networks = [ipaddress.ip_network(cidr, strict=False) for cidr in dest_cidrs]
            else:
                dest_networks = []
        except ValueError as e:
            print(f"Error in CIDR processing: {e}")
            sys.exit(1)

        if not from_ip_collections and not to_ip_collections and not from_workload_group and not to_workload_group:
            if any(net.prefixlen == 32 for net in source_networks) and any(net.prefixlen == 32 for net in dest_networks):
                print("Error: Both source and destination cannot contain /32 addresses.")
                sys.exit(1)

            source_ips = [net.network_address + 1 if net.prefixlen != 32 else net.network_address for net in source_networks]
            dest_ips = [net.network_address + 1 if net.prefixlen != 32 else net.network_address for net in dest_networks]

            for rule_num in range(int(num_rules)):
                source_ip_list = [str(source_ip) for source_ip in source_ips]
                dest_ip_list = [str(dest_ip) for dest_ip in dest_ips]

                rule = {
                    "apps": apps.split(","),
                    "action": action,
                    "from-ip-addresses": source_ip_list,
                    "to-ip-addresses": dest_ip_list,
                    "name": f"{args.name}_rule_{i+1}_{rule_num+1}",
                    "disable": False
                }
                policy_data["spec"]["rules"].append(rule)

                for idx, net in enumerate(source_networks):
                    if net.prefixlen != 32:
                        source_ips[idx] = increment_ip(source_ips[idx], 1)
                for idx, net in enumerate(dest_networks):
                    if net.prefixlen != 32:
                        dest_ips[idx] = increment_ip(dest_ips[idx], 1)
        else:
            rule = {
                "apps": apps.split(","),
                "action": action,
                "from-ipcollections": from_ip_collections.split(",") if from_ip_collections else None,
                "to-ipcollections": to_ip_collections.split(",") if to_ip_collections else None,
                "from-workload-groups": from_workload_group.split(",") if from_workload_group else None,
                "to-workload-groups": to_workload_group.split(",") if to_workload_group else None,
                "name": f"{args.name}_rule_{i+1}",
                "disable": False
            }
            rule = {k: v for k, v in rule.items() if v is not None}
            policy_data["spec"]["rules"].append(rule)

        table_data.append([
            i + 1,
            apps,
            action,
            from_ip_collections,
            to_ip_collections,
            from_workload_group,
            to_workload_group,
            ','.join(source_cidrs) if source_cidrs else 'N/A',
            ','.join(dest_cidrs) if dest_cidrs else 'N/A',
            num_rules
        ])

# Save the generated JSON to a local file if prompted
if args.save_json:
    with open(args.save_json, 'w') as file:
        json.dump(policy_data, file, indent=4)
    print(f"Policy data saved to {args.save_json}")

# Post the policy to PSM
status_code, response = post_policy_to_psm(token, policy_data)
if status_code == 200:
    print(f"Policy {policy_data['meta']['name']} added successfully.")
else:
    print(f"Failed to add policy {policy_data['meta']['name']}. Response: {response}")

# Print the summary table
if 'iterations_data' in locals():  # Check if iterations_data is defined
    headers = ["Iteration", "Apps", "Action", "From IP Collections", "To IP Collections", "From Workload Group", "To Workload Group", "Source CIDRs", "Destination CIDRs", "Number of Rules"]
    print(f"\nSummary of Configurations for Policy: {args.name}")
    print(tabulate(table_data, headers=headers, tablefmt="pretty"))

    # Print the total number of rules
    print(f"\nTotal number of rules created: {total_rules}")