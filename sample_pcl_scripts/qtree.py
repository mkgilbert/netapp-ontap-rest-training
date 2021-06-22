#! /usr/bin/env python3.7

"""
ONTAP 9.7 REST API Python Client Library Scripts
This script performs the following:
        - Create a qtree
        - List all volumes
        - Move a volume to another aggregate
        - Resize a volume to a new (bigger) size
        - Delete a volume

usage: python3.7 volume.py [-h] -c CLUSTER -v VOLUME_NAME -vs VSERVER_NAME -a AGGR_NAME -ma MOVE_AGGR_NAME
               -rs VOLUME_RESIZE -s VOLUME_SIZE [-u API_USER] [-p API_PASS]
The following arguments are required: -c/--cluster, -v/--volume_name, -vs/--vserver_name,
                -a/--aggr_name, -ma/--move_aggr_name, -rs/--volume_resize, -s/--volume_size
"""

import argparse
from getpass import getpass
import logging

from netapp_ontap import config, HostConnection, NetAppRestError
from netapp_ontap.resources import Qtree, QuotaRule, QosPolicy
from netapp_ontap.models import VolumeMovement

# Qtrees
def make_qtree(qtree_name: str, vserver_name: str, volume_name: str) -> None:
    """Creates a new volume in a SVM"""

    data = {
        'name': qtree_name,
        'svm': {'name': vserver_name},
        'volume': {'name': volume_name}
    }

    qtree = Qtree(**data)

    try:
        qtree.post()
        print("Qtree %s created successfully" % qtree.name)
    except NetAppRestError as err:
        print("Error: Qtree was not created: %s" % err)
    return

def list_qtrees(vserver_name: str, vol_name: str) -> None:
    """List qtrees in a volumes """

    print ("\nList of Qtrees:-")
    try:
        for qtree in Qtree.get_collection(**{"svm.name": vserver_name, "volume.name": vol_name}):
            qtree.get()
            print (qtree.name)
    except NetAppRestError as err:
        print("Error: Qtree list was not created: %s" % err)
    return

def get_qtree(volume_name: str, qtree_name: str) -> None:
    """Get the details of a qtree"""

    qtree = Qtree.find(**{"volume.name": volume_name, "name": qtree_name})

    try:
        qtree.get()
        print (qtree.name)
        print("Qtree details for %s obtained successfully" % qtree.name)
    except NetAppRestError as err:
        print("Error: Qtree details not obtained: %s" % err)
    return

def delete_qtree(volume_name: str, qtree_name: str) -> None:
    """Delete a qtree in a SVM"""

    qtree = Qtree.find(**{'name': qtree_name, 'volume.name': volume_name})

    try:
        qtree.delete()
        print("Qtree %s deleted successfully" % qtree.name)
    except NetAppRestError as err:
        print("Error: Qtree was not deleted: %s" % err)
    return

# Quota Rules
def make_quota_rule(vserver_name, volume_name, qtree_name, size, user):
    qr_data = {
        "svm": {"name": vserver_name},
        "volume": {"name": volume_name},
        "type": "user",
        "users": [{"name": user}],
        "qtree": {"name": qtree_name},
        "space": {"hard_limit": size}
    }
    qr = QuotaRule(**qr_data)
    try:
        qr.post()
        print("Qtree quota rule created for qtree %s" % qtree_name)
    except NetAppRestError as err:
        print(err)
        print("Error: Qtree quota rule not created for qtree %s" % qtree_name)
    return

# QoS
def make_qos_policy(vserver_name, qos_name):
    qos_data = {
        "svm": {"name": vserver_name},
        "name": qos_name,
        "adaptive": {
            "expected_iops": 100,
            "peak_iops": 200,
            "absolute_min_iops": 1
        }
    }
    try:
        qos = QosPolicy(**qos_data)
        qos.post()
        print("QoS Policy %s created" % qos_name)
    except NetAppRestError as err:
        print(err)
        print("Error: QoS policy %s was not created" % qos_name)
    return
    
def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create a new volume."
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details"
    )
    parser.add_argument(
        "-v", "--volume-name", required=True, help="Volume to create the qtree on"
    )
    parser.add_argument(
        "-vs", "--vserver-name", required=True, help="SVM to create the volume from"
    )
    parser.add_argument(
        "-q", "--qtree-name", required=True, help="Qtree to create"
    )
    parser.add_argument(
        "-qos", "--qos-policy", required=True, help="QoS Policy to create"
    )
    parser.add_argument(
        "-sh", "--space-hard-limit", required=True, help="Quota disk limit"
    )
    parser.add_argument(
        "-un", "--username", required=True, help="Username of the person to set quota for"
    )
    parser.add_argument("-u", "--api-user", default="admin", help="API Username")
    parser.add_argument("-p", "--api-pass", help="API Password")
    parsed_args = parser.parse_args()

    # collect the password without echo if not already provided
    if not parsed_args.api_pass:
        parsed_args.api_pass = getpass()

    return parsed_args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    args = parse_args()
    config.CONNECTION = HostConnection(
        args.cluster, username=args.api_user, password=args.api_pass, verify=False,
    )

    # Create a Volume
    make_qtree(args.qtree_name, args.vserver_name,args.volume_name)

    # List all volumes in the VServer
    #list_qtrees(args.vserver_name, args.volume_name)

    # Get the volume details
    get_qtree(args.volume_name, args.qtree_name)

    make_quota_rule(args.vserver_name, args.volume_name, args.qtree_name, args.space_hard_limit, args.username)

    make_qos_policy(args.vserver_name, args.qos_policy)