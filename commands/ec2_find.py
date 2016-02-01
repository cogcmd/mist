#!/usr/bin/env python

import boto.ec2
from boto.exception import EC2ResponseError
from boto.ec2.instance import Instance
import mist.cog as cog

def update_dict(data, key, value):
    if data.has_key(key):
        existing = data[key]
        data[key] = existing.append(value)
    else:
        data[key] = [value]
    return data

def parse_tags(tags, filters):
    if tags is not None:
        pairs = tags.split(",")
        for pair in pairs:
            parsed = pair.split("=")
            if len(parsed) == 2:
                key = "tag:" + parsed[0]
                update_dict(filters, key, parsed[1])
            else:
                if parsed[0] == "":
                    update_dict(filters, "tag-value", parsed[1])
                else:
                    update_dict(filters, "tag-key", parsed[0])
    return filters

def build_filters():
    filters = {}
    if cog.has_option("ami"):
        filters["image_id"] = cog.get_option("ami")
    filters = parse_tags(cog.get_option("tags"), filters)
    return filters

def filter_returned_data(instances, returned_fields, region_name, display_instances):
    for instance in instances:
        di = {}
        for field in returned_fields:
            field = field.strip()
            if field == "id":
                di["id"] = instance.id
            elif field == "pubdns":
                di["pubdns"] = instance.public_dns_name
            elif field == "privdns":
                di["privdns"] = instance.private_dns_name
            elif field == "state":
                di["state"] = instance.state
            elif field == "keyname":
                di["keyname"] = instance.key_name
            elif field == "ami":
                di["ami"] = instance.image_id
            elif field == "kernel":
                di["kernel"] = instance.kernel
            elif field == "arch":
                di["arch"] = instance.architecture
            elif field == "vpc":
                di["vpc"] = instance.vpc_id
            elif field == "pubip":
                di["pubip"] = instance.ip_address
            elif field == "privip":
                di["privip"] = instance.private_ip_address
            elif field == "az":
                di["az"] = instance.placement
            elif field == "type":
                di["type"] = instance.instance_type
        di["region"] = region_name
        display_instances.append(di)

if __name__ == "__main__":
    region_name = cog.get_option("region")
    try:
        returned_fields = cog.get_option("return")
        if returned_fields is None:
            returned_fields = "id,pubdns,privdns,state,keyname,ami,kernel,arch,vpc,pubip,privip,az,type"
        display_instances = []
        region = boto.ec2.connect_to_region(region_name)
        instances = region.get_only_instances(filters=build_filters())
        filter_returned_data(instances, returned_fields.split(","), region_name, display_instances)

        if display_instances == []:
            display_instances = ["none"]
        cog.send_json(display_instances)
    except EC2ResponseError as e:
        cog.send_text("Error accessing region %s: %s" % (region_name, e.message))
