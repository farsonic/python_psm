## Python scripts to added address objects and policies/rules to PSM 

The following scripts are intended for lab testing use only and are not supported by me. 

Example 1: Adding a Policy with Source and Destination IP Addresses

```
python3 psm_add_policy.py --name "TestPolicy" --apps "HTTP" --action "permit" --from-source-ip "192.168.1.0/24" --to-destination-ip "192.168.2.0/24" --description "Test policy for HTTP traffic" 
```

Example 2: Adding a Policy with Workload Groups
```
python3 psm_add_policy.py --name "WorkloadPolicyblah" --apps "HTTPS,SSH" --action "deny" --from-workload-group "vmgroup1,vmgroup2" --to-workload-group "vmgroup2" --description "Deny HTTPS traffic between vmgroup1/vmgroup2 and vmgroup2" 
```




