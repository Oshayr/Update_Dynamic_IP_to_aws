#!/usr/bin/python3
"""
Update your aws security group with your current ip
"""

from boto3 import resource
# requires boto3 to be configured
from requests import get

# region security group is in
AWS_REGION = "us-east-1"
# id of security group
SECURITY_GROUP_ID = "sg-12345a6bc7de89f10"
# description comment of the ip to be added or updated
DESCRIPTION = "dynamic ip"
# port to use - meaningless if protocol all, but still required
PORT = 22
# protocol tcp/udp/All ( -1 for All )
PROTOCOL = "-1"
# if true will remove current ip using the set Protocol,
# and port (if not all), even without the set description
REMOVE_CURRENT_MANUALLY_ADDED_IP = False


def get_old_ip(security_group_obj, current_ip):
    """
    Loop over aws security group ips for current ip or set description
    :param security_group_obj: aws security group obj
    :param current_ip: current ip
    :return: ip from security group that has the set description, or is the current ip if remove_ip is True
    """
    for permission in security_group_obj.ip_permissions:
        for ip_range in permission.get("IpRanges"):
            if DESCRIPTION in ip_range.get("Description", ""):
                return ip_range.get("CidrIp")
            if current_ip == ip_range.get("CidrIp") and permission.get('IpProtocol') == PROTOCOL and \
                    (PROTOCOL == '-1' or permission.get('FromPort') == PORT):
                assert not REMOVE_CURRENT_MANUALLY_ADDED_IP, \
                    ValueError(f' {current_ip} already exists in the security group')
                return ip_range.get("CidrIp")
    return None


# Get current ip
resp = get("http://checkip.amazonaws.com/")
resp.raise_for_status()
ip = resp.content.strip().decode("utf-8") + "/32"
assert ip, ValueError('No Current IP found')
# Get aws security group object
security_group = resource("ec2", region_name=AWS_REGION).SecurityGroup(SECURITY_GROUP_ID)
# Get from the aws security group, the ip and remove if needed
old_ip = get_old_ip(security_group, ip)
if old_ip:
    security_group.revoke_ingress(IpProtocol=PROTOCOL, FromPort=PORT, CidrIp=old_ip)
# Add current ip
ip_dir = {"FromPort": PORT, "IpProtocol": PROTOCOL, "IpRanges": [{"CidrIp": ip, "Description": DESCRIPTION}]}
security_group.authorize_ingress(IpPermissions=[ip_dir])
