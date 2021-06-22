#!/usr/bin/env python3.7
from netapp_ontap import config, HostConnection
from netapp_ontap.resources import Aggregate
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
conn = HostConnection("192.168.0.111", username = "admin", password = "Netapp1!", verify = False)
config.CONNECTION = conn  

def get_aggrs():
    aggrs = Aggregate.get_collection()
    for a in aggrs:
        print(f"Aggregate: {a.name}")

def create_aggr(name, disk_count, node_name):
    aggr_info = {
        "name": name,
        "node": {
            "name": node_name
        },
        "block_storage": {
            "primary": {
                "disk_count": disk_count,
                "raid_type": "raid_dp"
            }
        }
    }

    try:
        aggr = Aggregate(**aggr_info)
        aggr.post()
    except Exception as e:
        print(f"Error: {e}")
    

create_aggr("aggr1", 5, "cluster1-01" )
get_aggrs()