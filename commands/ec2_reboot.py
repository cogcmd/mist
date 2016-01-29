#!/usr/bin/env python


import os
import boto.ec2

def send_json(data):
    print "JSON\n"
    print "%s\n" % (json.dumps(data))

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
    image_id = os.getenv("COG_OPT_AMI")
    if image_id is not None:
        filters["image_id"] = image_id
    tags = os.getenv("COG_OPT_TAGS")
    filters = parse_tags(tags, filters)
    return filters

if __name__ == "__main__":
    region_name = os.getenv("COG_OPT_REGION")
    region = boto.ec2.connect_to_region(region_name)
    instances = region.get_only_instances(filters=build_filters())
    display_instances = []
    for instance in instances:
        display_instances.append({"id": instance.id,
                                  "state": instance.state,
                                  "ami": instance.image_id,
                                  "private_addr": instance.private_ip_address})
    if display_instances == []:
        display_instances = ["none"]
    send_json(display_instances)
