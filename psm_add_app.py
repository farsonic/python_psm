import json
import requests
import psm
import sys
import urllib3
import argparse

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize the argument parser
parser = argparse.ArgumentParser(description='Add or delete an application in PSM')
parser.add_argument('--add-app', action='store_true', help='Flag to add an application')
parser.add_argument('--del-app', action='store_true', help='Flag to delete an application')
parser.add_argument('--name', type=str, required=True, help='Name of the application')
parser.add_argument('--definition', action='append', help='Application definition in the form "protocol:port" or "protocol:port-range"')

# Parse the command line arguments
args = parser.parse_args()

# Obtain the token
token = psm.ObtainPSMToken()

# Function to post the application to PSM
def post_app_to_psm(token, app_name, definitions):
    psmipaddress = json.load(open('config.json'))['psmipaddress']
    url = f"https://{psmipaddress}/configs/security/v1/tenant/default/apps"
    headers = psm.constructHeader(token)
    proto_ports = [{'protocol': d['protocol'], 'ports': d['port']} for d in definitions]
    app_data = {
        "kind": None,
        "api-version": None,
        "meta": {
            "name": app_name,
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
            "proto-ports": proto_ports,
            "timeout": None
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(app_data), verify=False)
    return response.status_code, response.json()

# Function to delete the application from PSM
def delete_app_from_psm(token, app_name):
    psmipaddress = json.load(open('config.json'))['psmipaddress']
    url = f"https://{psmipaddress}/configs/security/v1/tenant/default/apps/{app_name}"
    headers = psm.constructHeader(token)
    response = requests.delete(url, headers=headers, verify=False)
    return response.status_code, response.json()

# Add application
if args.add_app:
    if not args.definition:
        print("Error: --definition argument is required when using --add-app.")
        sys.exit(1)

    # Process definitions
    definitions = []
    for definition in args.definition:
        protocol, port = definition.split(':')
        definitions.append({
            'protocol': protocol.upper(),
            'port': port
        })

    # Post the application to PSM
    status_code, response = post_app_to_psm(token, args.name, definitions)
    if status_code == 200:
        print(f"Application {args.name} added successfully.")
    else:
        print(f"Failed to add application {args.name}. Response: {response}")

# Delete application
if args.del_app:
    status_code, response = delete_app_from_psm(token, args.name)
    if status_code == 200:
        print(f"Application {args.name} deleted successfully.")
    else:
        print(f"Failed to delete application {args.name}. Response: {response}")
