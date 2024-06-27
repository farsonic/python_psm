## Python scripts to added address objects and policies/rules to PSM 

The following scripts are intended for lab testing use only and are not supported by me but should serve as a good example to push application objects and various policies to PSM and then subsequently into attached CX10000 switches under management. 

Currently there is four scripts to allow for 

* Authentication to PSM and Token collection   (psm.py)
* Application definition creation and deletion (psm_app.py)
* Single policy and rule creation and deletion (psm_add_policy.py) 
* Bulk policy and rule creation                (psm_add_bulk_rules.py) 




#### Policy with Source and Destination IP Addresses
```
python3 psm_policy.py --add-policy --name "TestPolicy" --apps "HTTPS" --action "permit" --from-source-ip "192.168.1.0/24" --to-destination-ip "192.168.2.0/24" --description "Permit policy for HTTPS traffic"
python3 psm_policy.py --del-policy --name "TestPolicy"
```


#### Policy with Workload Groups
```
python3 psm_policy.py --add-policy --name "WorkloadPolicy" --apps "HTTPS,SSH" --action "deny" --from-workload-group "vmgroup1,vmgroup2" --to-workload-group "vmgroup2" --description "Deny HTTPS traffic"
python3 psm_policy.py --del-policy --name "WorkloadPolicy" 
```


#### Policy with IP Collections
```
python3 psm_policy.py --add-policy --name "IPCollectionPolicy" --apps "DNS" --action "permit" --from-ip-collections "Group1,Group2" --to-ip-collections "Group2" --description "Permit DNS traffic between CollectionA and CollectionB"
python3 psm_policy.py --del-policy --name "IPCollectionPolicy"
```


#### Policy with Debug Mode Enabled
```
python psm_policy.py --add-policy --name "DebugPolicy" --apps "FTP" --action "permit" --from-source-ip "10.0.0.0/24" --to-destination-ip "10.0.1.0/24" --description "Permit FTP traffic with debug mode"  --debug
python psm_policy.py --del-policy --name "DebugPolicy" 
```

#### Policy with combinations
```
python3 psm_add_policy.py --name "CombinationPolicy" --apps "DNS" --action "permit" --from-ip-collections "Group1,Group2" --to-workload-group "vmgroup2" --from-source-ip "192.168.1.0/24" --to-destination-ip "192.168.2.0/24,192.168.2.10/24" --description "Permit traffic between combination"
```
