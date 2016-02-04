#!/usr/bin/env python

import boto.ec2
from boto.exception import EC2ResponseError
import mist.cog as cog

def parse_tags(tags):
    parsed = {}
    if tags is not None:
        pairs = tags.split(",")
        for pair in pairs:
            kv = pair.split("=")
            if len(parsed) == 2:
               parsed[kv[0]] = kv[1]
            else:
                parsed[kv[0]] = ""
    if len(parsed) == 0:
        return None
    else:
        return parsed

def tag_instances(region, instance_ids, tags):
    instances = region.get_only_instances(instance_ids = instance_ids)
    for instance in instances:
        instance.add_tags(tags)

def create_instance(region_name, ami, instance_type, count, keypair, az = None, subnet = None, user_data = None, tags = None):
    region = boto.ec2.connect_to_region(region_name)
    reservation = region.run_instances(ami, min_count=count, max_count=count, instance_type=instance_type, placement=az,
                                       key_name=keypair, subnet_id=subnet, user_data=user_data)
    instance_ids = [instance.id for instance in reservation.instances]
    if tags is not None:
        tag_instances(region, instance_ids, tags)
    cog.send_json({"instances": instance_ids})

if __name__ == "__main__":
    region_name = cog.get_option("region")
    instance_type = cog.get_option("type")
    ami = cog.get_option("ami")
    keypair = cog.get_option("keypair")
    az = cog.get_option("az")
    subnet = cog.get_option("subnet")
    user_data = cog.get_option("user-data")
    tags = parse_tags(cog.get_option("tags"))
    count = int(cog.get_option("count", "1"))
    try:
        create_instance(region_name, ami, instance_type, count, keypair=keypair,
                        az=az, subnet=subnet, user_data=user_data, tags=tags)
    except EC2ResponseError as e:
        cog.send_error("Error starting new instance: %s" % (e.message))
