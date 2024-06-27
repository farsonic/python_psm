## Python scripts to added address objects and policies/rules to PSM 

The following scripts are intended for lab testing use only and are not supported by me but should serve as a good example to push application objects and various policies to PSM and then subsequently into attached CX10000 switches under management. 

Currently there is four scripts to allow for the following capabilities. 

* Authentication to PSM and Token collection   (psm.py)
* Application definition creation and deletion (psm_app.py)
* Single policy and rule creation and deletion (psm_add_policy.py) 
* Bulk policy and rule creation                (psm_add_bulk_rules.py) 


## Requirements

* Python 3.x
* `requests` library
* `psm.py` module for obtaining the PSM token



## JSON Configuration File

Each of these scripts leverages the psm.py script as a Python module to authenticate to the PSM server and retrieve the authentication token that is used for all subsequent REST commanded issued to the PSM server. There should be a file called config.json in the same directory that has the details of the PSM server IP/Host name as well as authentication details. This file should be in the following format. 

```
{
  "psmipaddress": "X.X.X.X",
  "psmusername": "admin",
  "psmpassword": "Pensando0$"
}
```



## Creation and deletion of a single policy. 

This script will quickly allow for the creation of a security policy within PSM. This policy is not attached by default to an existing VRF or a network and will be the responsibility of the operator to assign this as well as perform any network redirection to have traffic pass through the policy. When policy is pushed to PSM it is done as a single PUT of the entire policy and doesn't allow for a PATCH function. Therefore this example really only allows for the creation of a single rule for each policy. For adding bulk rules please refer to the additional script below. 

The following examples allow for the creation and deletion of a single policy/rule into the configured PSM server. There are several options that can be leveraged 

OPTIONS
       --add-app
              Flag to add an application.

       --del-app
              Flag to delete an application.

       --add-policy
              Flag to add a policy.

       --del-policy
              Flag to delete a policy.

       --name NAME
              Name of the application or policy (required).

       --definition DEFINITION
              Application definition in the form "protocol:port" or "protocol:port-range".

       --apps APPS
              Comma-separated list of application names for the policy.

       --action ACTION
              Action for the policy (permit or deny).

       --from-source-ip IP_ADDRESSES
              Comma-separated list of source IP addresses.

       --to-destination-ip IP_ADDRESSES
              Comma-separated list of destination IP addresses.

       --from-workload-group GROUPS
              Comma-separated list of from workload groups.

       --to-workload-group GROUPS
              Comma-separated list of to workload groups.

       --description DESCRIPTION
              Description of the policy.

       --disable
              Disable flag for the policy.

       --from-ip-collections COLLECTIONS
              Comma-separated list of from IP collections.

       --to-ip-collections COLLECTIONS
              Comma-separated list of to IP collections.

       --priority PRIORITY
              Priority of the policy.

       --policy-dist-target TARGET
              Policy distribution targets.

       --debug
              Enable debug mode.


#### Examples
```
python3 psm_policy.py --add-policy --name "TestPolicy" --apps "HTTPS" --action "permit" --from-source-ip "192.168.1.0/24" --to-destination-ip "192.168.2.0/24" --description "Permit policy for HTTPS traffic"
python3 psm_policy.py --del-policy --name "TestPolicy"


python3 psm_policy.py --add-policy --name "WorkloadPolicy" --apps "HTTPS,SSH" --action "deny" --from-workload-group "vmgroup1,vmgroup2" --to-workload-group "vmgroup2" --description "Deny HTTPS traffic"
python3 psm_policy.py --del-policy --name "WorkloadPolicy" 


python3 psm_policy.py --add-policy --name "IPCollectionPolicy" --apps "DNS" --action "permit" --from-ip-collections "Group1,Group2" --to-ip-collections "Group2" --description "Permit DNS traffic between CollectionA and CollectionB"
python3 psm_policy.py --del-policy --name "IPCollectionPolicy"


python psm_policy.py --add-policy --name "DebugPolicy" --apps "FTP" --action "permit" --from-source-ip "10.0.0.0/24" --to-destination-ip "10.0.1.0/24" --description "Permit FTP traffic with debug mode"  --debug
python psm_policy.py --del-policy --name "DebugPolicy" 


python3 psm_add_policy.py --name "CombinationPolicy" --apps "DNS" --action "permit" --from-ip-collections "Group1,Group2" --to-workload-group "vmgroup2" --from-source-ip "192.168.1.0/24" --to-destination-ip "192.168.2.0/24,192.168.2.10/24" --description "Permit traffic between combination"
```
