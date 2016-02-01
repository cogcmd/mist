#!/usr/bin/env python

import boto.vpc
from boto.exception import EC2ResponseError
import mist.cog as cog

def build_subnet_list(subnets):
    retval = []
    for subnet in subnets:
        retval.append({"id": subnet.id,
                       "az": subnet.availability_zone,
                       "az_default": subnet.defaultForAz,
                       "cidr_block": subnet.cidr_block,
                       "available_addrs": subnet.available_ip_address_count})
    return retval

def vpc_list(region_name, ids):
    vpcs = []
    filters = {"state": "available"}
    if len(ids) == 0:
        ids = None
    region = boto.vpc.connect_to_region(region_name)
    for vpc in region.get_all_vpcs(ids, filters=filters):
        subnets = region.get_all_subnets(filters={"vpcId": vpc.id})
        vpcs.append({"id": vpc.id,
                     "state": vpc.state,
                     "cidr_block": vpc.cidr_block,
                     "region": region_name,
                     "subnets": build_subnet_list(subnets)})
    if len(vpcs) == 0:
        vpcs = ["none"]
    cog.send_json(vpcs)


if __name__ == "__main__":
    region_name = cog.get_option("region")
    try:
        if cog.command_name() == "vpc-list":
            vpc_list(region_name, cog.collect_args())
    except EC2ResponseError as e:
        cog.send_text("Error listing VPCs: %s" % (e.message))
