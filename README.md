# Python scripts to added address objects and policies/rules to PSM 

The following scripts are intended for lab testing use only and are not supported by me but should serve as a good example to push application objects and various policies to PSM and then subsequently into attached CX10000 switches under management. The code was written and iterated and it is possible there is some redundant functions - especially in the bulk addition code :) 

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

#### Examples 
```
python3 psm_app.py --add-app --name "myapp" --definition "udp:6789-6800" --definition "tcp:555-556"
python3 psm_app.py --del-app --name "myapp"
```

### Creation and deletion of a single policy/rule

This script will quickly allow for the creation or deletion of a security policy within PSM. This policy is not attached by default to an existing VRF or a network and will be the responsibility of the operator to assign this as well as perform any network redirection to have traffic pass through the policy. When policy is pushed to PSM it is done as a single PUT of the entire policy and doesn't allow for a PATCH function. Therefore this example really only allows for the creation of a single rule for each policy. For adding bulk rules please refer to the additional script below. 

The following examples allow for the creation and deletion of a single policy/rule into the configured PSM server. There are several options that can be leveraged and the script should accommodate multiple --source and --destination options of each type. If there is no entry provided for a --source or --destination then the value should be set to ANY. I've not tested every combination so let me know if some don't work. 

Use the --help option to see all available arguments. 

#### Examples
```
python3 psm_policy.py --add-policy --name "norules"
python3 psm_policy.py --del-policy --name "norules"

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

### Creation and deletion of a single Policy with Bulk rule addition

In order to attach multiple rules to a single policy the psm_policy script was modified to allow for multiple rules to be added to a single policy using an external CSV file as the source of the data. In order for this policy to be created you will first need to create an empty policy using the above psm_policy.py script. This script can also save and load the generated JSON file and push this directly to PSM also, this could be used for A/B testing between a changing set of rules within a single policy. 

#### File format 

The CSV file can be saved with any name required for testing and the columns are ; seperated (allowing for mutlople apps etc using a comma) and should be specified in the following format and should have this example as the header. An example file (bulkrules.json) is included in the respostory 

```
apps;action;from_ip_collections;to_ip_collections;from_workload_group;to_workload_group;source_cidrs;dest_cidrs;num_rules
```

Each column represents the following values 

* apps                  - A comma separated list of applications. Applications need to already exist in PSM 
* action                - Either permit or deny 
* from_ip_collections   - A comma separated list of IP collections. IP Collections need to already exist in PSM 
* to_ip_collections     - A comma separated list of IP collections. IP Collections need to already exist in PSM 
* from_workload_group   - A comma separated list of VMware Workload Grops. Workload groups need to already exist in PSM 
* to_workload_group     - A comma separated list of VMware Workload Grops. Workload groups need to already exist in PSM 
* source_cidrs          - A comma separated list of subnets with a default of /32 if a mask isn't provided. If a /32 is provided the num_rules is always 1 
* dest_cidrs            - A comma separated list of subnets with a default of /32 if a mask isn't provided. If a /32 is provided the num_rules is always 1
* num_rules             - Number of unique source/destination rules to create from the provided non /32 subnets provided in the CIDR ranges. 

#### Examples
```
python3 psm_add_policy_test.py --add-policy --name "BigPolicy_VLAN100"
python3 psm_add_bulk_rules.py --name "BigPolicy_VLAN100" --import-csv bulkrules.csv --save-json vlan100_A.json

python3 psm_add_bulk_rules.py --name "BigPolicy_VLAN100" --load-json vlan100_A.json
```

This will create the following 

```
Policy data saved to vlan100_A.json
Policy BigPolicy_VLAN100 added successfully.
Summary of Configurations for Policy: BigPolicy_VLAN100
+-----------+--------------------+--------+---------------------+-------------------+---------------------+-------------------+-------------------------+-------------------+-----------------+
| Iteration |        Apps        | Action | From IP Collections | To IP Collections | From Workload Group | To Workload Group |      Source CIDRs       | Destination CIDRs | Number of Rules |
+-----------+--------------------+--------+---------------------+-------------------+---------------------+-------------------+-------------------------+-------------------+-----------------+
|     1     |   HTTPS,DNS,SSH    | permit |                     |                   |                     |                   | 10.1.0.0/16,11.1.0.0/16 |   10.101.0.0/16   |      1000       |
|     2     |   HTTPS,DNS,SSH    |  deny  |                     |                   |                     |                   | 1.1.1.1/32,10.2.0.0/16  |   10.102.0.0/16   |      1000       |
|     3     |   HTTPS,DNS,SSH    | permit |                     |                   |                     |                   |       10.3.0.0/16       |   10.103.0.0/16   |      1000       |
|     4     |   HTTPS,DNS,SSH    |  deny  |                     |                   |                     |                   |       10.4.0.0/16       |   10.103.0.0/16   |      1000       |
|     5     |   HTTPS,DNS,SSH    | permit |                     |                   |                     |                   |       10.5.0.0/16       |   10.104.0.0/16   |      1000       |
|     6     |   HTTPS,DNS,SSH    |  deny  |                     |                   |                     |                   |       10.6.0.0/16       |   10.105.0.0/16   |      1000       |
|     7     |   HTTPS,DNS,SSH    | permit |                     |                   |                     |                   |       10.7.0.0/16       |   10.106.0.0/16   |      1000       |
|     8     |   HTTPS,DNS,SSH    |  deny  |                     |                   |                     |                   |       10.7.0.0/16       |   10.106.0.0/16   |      1000       |
|     9     | HTTPS,DNS,SSH,PING | permit |       Group1        |      Group2       |                     |                   |           N/A           |        N/A        |        1        |
|    10     | HTTPS,DNS,SSH,PING | permit |       Group1        |      Group2       |      vmgroup1       |     vmgroup2      |           N/A           |        N/A        |        1        |
+-----------+--------------------+--------+---------------------+-------------------+---------------------+-------------------+-------------------------+-------------------+-----------------+

Total number of rules created: 8002
```

When the bulk addition runs if performs a HTTP PUT of the entire JSON structure for the assigned policy to PSM. This will override all existing rules and push this down to the assocaited DSMs where needed.  

