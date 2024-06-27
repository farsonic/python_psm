# Python scripts to added address objects and policies/rules to PSM 

The following scripts are intended for lab testing use only and are not supported by me but should serve as a good example to push application objects and various policies to PSM and then subsequently into attached CX10000 switches under management. 

Currently there is four scripts to allow for the following capabilities. 

* Authentication to PSM and Token collection   (psm.py)
* Application definition creation and deletion (psm_app.py)
* Single policy and rule creation and deletion (psm_add_policy.py) 
* Bulk policy and rule creation                (psm_add_bulk_rules.py) 


# Requirements

* Python 3.x
* `requests` library
* `psm.py` module for obtaining the PSM token



##  Configuration File

Each of these scripts leverages the psm.py script as a Python module to authenticate to the PSM server and retrieve the authentication token that is used for all subsequent REST commanded issued to the PSM server. There should be a file called config.json in the same directory that has the details of the PSM server IP/Host name as well as authentication details. This file should be in the following format. 

```
{
  "psmipaddress": "X.X.X.X",
  "psmusername": "admin",
  "psmpassword": "Pensando0$"
}
```
### Creation and deletion of a single application definition 

This script will quickly allow for the creation or deletion of an application object within PSM. The application defintition itself does nothing until it is attached to a rule within a security policy. The application creation process should allow for complex application definition creation using multiple protocols and source/destination numbers. 



### Creation and deletion of a single policy

This script will quickly allow for the creation or deletion of a security policy within PSM. This policy is not attached by default to an existing VRF or a network and will be the responsibility of the operator to assign this as well as perform any network redirection to have traffic pass through the policy. When policy is pushed to PSM it is done as a single PUT of the entire policy and doesn't allow for a PATCH function. Therefore this example really only allows for the creation of a single rule for each policy. For adding bulk rules please refer to the additional script below. 

The following examples allow for the creation and deletion of a single policy/rule into the configured PSM server. There are several options that can be leveraged and the script should accommodate multiple --source and --destination options of each type. If there is no entry provided for a --source or --destination then the value should be set to ANY. I've not tested every combination so let me know if some don't work. 

Use the --help option to see all available arguments. 

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
