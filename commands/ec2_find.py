#!/usr/bin/env python

import boto.ec2
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

if __name__ == "__main__":
    region_name = cog.get_option("region")
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
    cog.send_json(display_instances)
