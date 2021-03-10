# Update_Dynamic_IP_to_aws

Simple Python updater of current IP to your aws security group.

Needs Boto3 configuration setup.

Fill in the settings at top of script:

| Setting | Example | Description |
| ------- | ------- | ----------- |
| AWS_REGION | us-east-1 | region security group is in |
| SECURITY_GROUP_ID | sg-12345a6bc7de89f10 | id of security group |
| DESCRIPTION | dynamic ip | description comment of the ip to be added or updated |
| PORT | 22 | port to use - meaningless if protocol all, but still required |
| PROTOCOL | For All use: -1 | protocol tcp/udp/All |
| REMOVE_CURRENT_MANUALLY_ADDED_IP | False | if true will remove current ip using the set Protocol, and port (if not all), if no set description | 
