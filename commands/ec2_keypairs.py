#!/usr/bin/env python

import boto.ec2
from boto.exception import EC2ResponseError
import mist.cog as cog

def keypairs_list(region_name):
    keypairs = []
    names = cog.collect_args()
    if len(names) == 0:
        names = None
    region = boto.ec2.connect_to_region(region_name)
    for kp in region.get_all_key_pairs(names):
        keypairs.append({"name": kp.name,
                         "region": region_name,
                         "fingerprint": kp.fingerprint})
    if len(keypairs) == 0:
        keypairs = ["none"]
    cog.send_json(keypairs)


if __name__ == "__main__":
    region_name = cog.get_option("region")
    try:
        if cog.command_name() == "keypairs-list":
            keypairs_list(region_name)
    except EC2ResponseError as e:
        cog.send_text("Error listing keypairs: %s" % (e.message))
