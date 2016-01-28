#!/usr/bin/env python

import json
import os
import boto.ec2

def send_json(data):
    print "JSON\n"
    print "%s\n" % (json.dumps(data))

if __name__ == "__main__":
    region_name = os.getenv("COG_OPT_REGION")
    region = boto.ec2.connect_to_region(region_name)
    instances = region.get_only_instances()
    display_instances = []
    for instance in instances:
        display_instances.append({"id": instance.id,
                                  "state": instance.state,
                                  "ami": instance.image_id,
                                  "private_addr": instance.private_ip_address})
    send_json(display_instances)
