#!/usr/bin/env python

import boto.ec2
import mist.cog as cog

def ec2_reboot(instances):
    region_name = cog.get_option("region")
    region = boto.ec2.connect_to_region(region_name)
    if len(instances) > 0:
        region.reboot_instances(instances)
    cog.send_json({"rebooted": len(instances)})

def ec2_stop(instances):
    region_name = cog.get_option("region")
    region = boto.ec2.connect_to_region(region_name)
    if len(instances) > 0:
        region.stop_instances(instances)
    cog.send_json({"stopped": len(instances)})

def ec2_start(instances):
    region_name = cog.get_option("region")
    region = boto.ec2.connect_to_region(region_name)
    if len(instances) > 0:
        region.start_instances(instances)
    cog.send_json({"started": len(instances)})

if __name__ == "__main__":
    command_name = cog.command_name()
    instances = cog.collect_args()
    if command_name == "ec2-reboot":
        ec2_reboot(instances)
    elif command_name == "ec2-stop":
        ec2_stop(instances)
    elif command_name == "ec2-start":
        ec2_start(instances)
    else:
        cog.send_error("I don't know how to %s" % (command_name))

