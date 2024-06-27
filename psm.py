import requests
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

def ObtainPSMToken():
    response = {}
    try:
        config = load_config()
        psmipaddress = config['psmipaddress']
        psmusername = config['psmusername']
        psmpassword = config['psmpassword']

        url = "https://" + psmipaddress + "/v1/login"
        credentials = {"username": psmusername, "password": psmpassword, "tenant": "default"}
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        response = requests.post(url, headers=headers, data=json.dumps(credentials), verify=False, timeout=5)
        headers = response.headers
        return headers['Set-Cookie']
    except ConnectionError:
        response.update({"message": "Connection error, no response from PSM"})
        return response
    except Exception as err:
        response.update({"message": "Failed to establish a connection to PSM"})
        return response

def constructHeader(token):
    headers = {}
    headers["Content-Type"] = "application/json"
    headers['accept'] = "application/json; version=1.0"
    headers["cookie"] = token
    return headers
