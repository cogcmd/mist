#!/usr/bin/env python

import boto.ec2
import mist.cog as cog

if __name__ == "__main__":
    region_name = cog.get_option("region")
    region = boto.ec2.connect_to_region(region_name)
    instances = cog.collect_args()
    if len(instances) > 0:
        region.terminate_instances(instances)
    cog.send_json({"terminated": len(instances)})
