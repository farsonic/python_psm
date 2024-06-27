import json
import requests
import psm
import sys
import urllib3
import argparse

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize the argument parser
parser = argparse.ArgumentParser(description='Add or delete a policy in PSM')
parser.add_argument('--add-policy', action='store_true', help='Flag to add a policy')
parser.add_argument('--del-policy', action='store_true', help='Flag to delete a policy')
parser.add_argument('--name', type=str, required=True, help='Name of the policy')
parser.add_argument('--apps', type=str, help='Comma-separated list of application names')
parser.add_argument('--action', type=str, choices=['permit', 'deny'], help='Action for the policy')
parser.add_argument('--from-source-ip', type=str, help='Comma-separated list of source IP addresses')
parser.add_argument('--to-destination-ip', type=str, help='Comma-separated list of destination IP addresses')
parser.add_argument('--from-workload-group', type=str, help='Comma-separated list of from workload groups')
parser.add_argument('--to-workload-group', type=str, help='Comma-separated list of to workload groups')
parser.add_argument('--description', type=str, help='Description of the policy')
parser.add_argument('--disable', type=bool, default=False, help='Disable flag for the policy')
parser.add_argument('--from-ip-collections', type=str, help='Comma-separated list of from IP collections')
parser.add_argument('--to-ip-collections', type=str, help='Comma-separated list of to IP collections')
parser.add_argument('--priority', type=int, default=10, help='Priority of the policy')
parser.add_argument('--policy-dist-target', type=str, help='Policy distribution targets')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')

# Parse the command line arguments
args = parser.parse_args()

# Obtain the token
token = psm.ObtainPSMToken()

if args.debug:
    print("Token obtained successfully.")

# Function to post the policy to PSM
def post_policy_to_psm(token, policy_data):
    psmipaddress = json.load(open('config.json'))['psmipaddress']
    url = f"https://{psmipaddress}/configs/security/v1/tenant/default/networksecuritypolicies"
    headers = psm.constructHeader(token)
    if args.debug:
        print("URL:", url)
        print("Headers:", headers)
        print("Policy Data JSON:", json.dumps(policy_data, indent=4))
    response = requests.post(url, headers=headers, data=json.dumps(policy_data), verify=False)
    return response.status_code, response.json()

# Function to delete the policy from PSM
def delete_policy_from_psm(token, policy_name):
    psmipaddress = json.load(open('config.json'))['psmipaddress']
    url = f"https://{psmipaddress}/configs/security/v1/tenant/default/networksecuritypolicies/{policy_name}"
    headers = psm.constructHeader(token)
    response = requests.delete(url, headers=headers, verify=False)
    return response.status_code, response.json()

# Add policy
if args.add_policy:
    # Split input arguments into lists if provided
    from_ip_addresses = args.from_source_ip.split(',') if args.from_source_ip else []
    to_ip_addresses = args.to_destination_ip.split(',') if args.to_destination_ip else []
    from_workload_groups = args.from_workload_group.split(',') if args.from_workload_group else []
    to_workload_groups = args.to_workload_group.split(',') if args.to_workload_group else []
    from_ip_collections = args.from_ip_collections.split(',') if args.from_ip_collections else []
    to_ip_collections = args.to_ip_collections.split(',') if args.to_ip_collections else []

    # Set default value to 'ANY' if no other from/to entries are defined
    if not from_ip_addresses and not from_workload_groups and not from_ip_collections:
        from_ip_addresses = ["ANY"]

    if not to_ip_addresses and not to_workload_groups and not to_ip_collections:
        to_ip_addresses = ["ANY"]

    # Split the apps argument into a list if provided
    apps_list = args.apps.split(",") if args.apps else []

    # Construct the rule
    rule = {
        "apps": apps_list,
        "action": args.action if args.action else None,
        "from-ip-addresses": from_ip_addresses,
        "to-ip-addresses": to_ip_addresses,
        "from-workload-groups": from_workload_groups if from_workload_groups else None,
        "to-workload-groups": to_workload_groups if to_workload_groups else None,
        "description": args.description if args.description else None,
        "name": args.name,
        "disable": args.disable if args.disable else None,
        "from-ipcollections": from_ip_collections if from_ip_collections else None,
        "to-ipcollections": to_ip_collections if to_ip_collections else None,
        "labels": None
    }

    # Filter out None values
    rule = {k: v for k, v in rule.items() if v is not None}

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
            "rules": [rule],
            "priority": args.priority if args.priority else None,
            "policy-distribution-targets": [
                args.policy_dist_target if args.policy_dist_target else "default"
            ]
        }
    }

    # Post the policy to PSM
    status_code, response = post_policy_to_psm(token, policy_data)
    if status_code == 200:
        print(f"Policy {args.name} added successfully.")
    else:
        print(f"Failed to add policy {args.name}. Response: {response}")

# Delete policy
if args.del_policy:
    status_code, response = delete_policy_from_psm(token, args.name)
    if status_code == 200:
        print(f"Policy {args.name} deleted successfully.")
    else:
        print(f"Failed to delete policy {args.name}. Response: {response}")
