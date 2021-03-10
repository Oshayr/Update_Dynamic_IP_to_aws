#!/usr/bin/python3

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
# if true will remove current ip using the set Protocol, and port (if not all), even without the set description
REMOVE_CURRENT_MANUALLY_ADDED_IP = False


def get_old_ip(sg, oip, protocol, port, disc, remove_ip):
    """
    Loop over aws security group ips for current ip or set description
    :param sg: aws security group obj
    :param oip: current ip
    :param protocol: user set protocol
    :param port: user set port
    :param disc: user set description
    :param remove_ip: Boolean if to remove the manually added current ip from the security group (needs to be removed
    in order to add current ip with set description)
    :return: ip from security group that has the set description, or is the current ip if remove_ip is True
    """
    for s in sg.ip_permissions:
        for r in s.get("IpRanges"):
            if disc in r.get("Description", ""):
                return r.get("CidrIp")
            if oip == r.get("CidrIp") and s.get('IpProtocol') == protocol and \
                    (protocol == '-1' or s.get('FromPort') == port):
                assert not remove_ip, ValueError(f' {oip} already exists in the security group')
                return r.get("CidrIp")
    return None


# Get current ip
resp = get("http://checkip.amazonaws.com/")
resp.raise_for_status()
ip = resp.content.strip().decode("utf-8") + "/32"
assert ip, ValueError('No Current IP found')
# Get aws security group object
security_group = resource("ec2", region_name=AWS_REGION).SecurityGroup(SECURITY_GROUP_ID)
# Get from the aws security group, the ip and remove if needed
if old_ip := get_old_ip(security_group, ip, PROTOCOL, PORT, DESCRIPTION, REMOVE_CURRENT_MANUALLY_ADDED_IP):
    security_group.revoke_ingress(IpProtocol=PROTOCOL, FromPort=PORT, CidrIp=old_ip)
# Add current ip
security_group.authorize_ingress(IpPermissions=[{"FromPort": PORT, "IpProtocol": PROTOCOL,
                                                 "IpRanges": [{"CidrIp": ip, "Description": DESCRIPTION}]}])
