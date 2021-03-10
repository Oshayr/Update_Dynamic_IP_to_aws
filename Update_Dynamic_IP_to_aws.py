import boto3
# requires boto3 to be setup

import requests

AWS_REGION = "us-east-1"  # region security group is in
security_group_id = "sg-XXXXXXXXXXXXXXXXX"  # id of security group
DISC = "dynamic ip"  # description comment of the ip to be added or updated
PORT = 22  # port to use - meaningless if protocol all, but still needed
PROTOCOL = "All"  # protocol tcp/udp/all
REMOVE_CURRENT_MANUALLY_ADDED_IP = False  # if true will remove current ip even without the description


def get_ip():
    """
    Get from web Current IP
    :return: IP <str>
    """
    resp = requests.get("http://checkip.amazonaws.com/")
    resp.raise_for_status()
    return resp.content.strip().decode("utf-8") + "/32"


def need_to_update(sg, ip):
    last_ip = None
    for s in sg.ip_permissions:
        for r in s.get("IpRanges"):
            if "dynamic ip" in r.get("Description", ""):
                last_ip = r.get("CidrIp")
            if ip == r.get("CidrIp"):
                if s["IpProtocol"] != "-1":
                    print(
                        f"{', '.join([f'{k}: {v}' for k, v in r.items()])} - Manually entered - "
                        f"Found with {s.get('IpProtocol')} Port: {s.get('FromPort')}"
                    )

                elif last_ip == ip:
                    print(
                        f"{', '.join([f'{k}: {v}' for k, v in r.items()])}- Manually entered - found with All Traffic"
                    )
                    if REMOVE_CURRENT_MANUALLY_ADDED_IP:
                        return True, ip
                    return False, None

    return True, last_ip


def add_ip(sg, ip):
    try:
        f = sg.authorize_ingress(
            IpPermissions=[
                {
                    "FromPort": PORT,
                    "IpProtocol": PROTOCOL,
                    "IpRanges": [{"CidrIp": ip, "Description": DISC}],
                }
            ]
        )
    except BaseException as e:
        print(e)
        f = False
    return f


def del_ip(sg, ip):
    try:
        f = sg.revoke_ingress(IpProtocol=PROTOCOL, FromPort=PORT, CidrIp=ip)
    except BaseException as e:
        print(e)
        f = False
    return f


current_ip = get_ip()
if not current_ip:
    print("No Current IP Found")
else:
    ec2 = boto3.resource("ec2", region_name=AWS_REGION)
    security_group = ec2.SecurityGroup(security_group_id)
    update, old_ip = need_to_update(security_group, current_ip)
    if update:
        if old_ip and del_ip(security_group, old_ip):
            print(f"Removed {old_ip}")
        if add_ip(security_group, current_ip):
            print(f"Updated {current_ip}")
