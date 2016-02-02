#!/usr/bin/env python

import boto.ec2
import mist.cog as cog

def parse_tags(tags):
    parsed = {}
    pairs = tags.split(",")
    for pair in pairs:
        kv = pair.split("=")
        if len(parsed) == 2:
            parsed[kv[0]] = kv[1]
        else:
            parsed[kv[0]] = ""
    return parsed

def add_tags(region_name, tags, ids):
    region = boto.ec2.connect_to_region(region_name)
    for instance in region.get_only_instances(instance_ids = ids):
        instance.add_tags(tags)
    cog.send_text("ok")

def remove_tags(region_name, tags, ids):
    region = boto.ec2.connect_to_region(region_name)
    for instance in region.get_only_instances(instance_ids = ids):
        instance.remove_tags(tags)
    cog.send_text("ok")

if __name__ == "__main__":
    region_name = cog.get_option("region")
    tags = parse_tags(cog.get_option("tags"))
    ids = cog.collect_args()
    if cog.get_option("remove"):
        remove_tags(region_name, tags, ids)
    else:
        add_tags(region_name, tags, ids)
