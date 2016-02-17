import boto.vpc

from cog.logger import Logger
from cog.command import Command


class VPCListCommand(Command):
    def build_subnet_list(self, subnets):
        retval = []
        for subnet in subnets:
            retval.append({"id": subnet.id,
                           "az": subnet.availability_zone,
                           "az_default": subnet.defaultForAz,
                           "cidr_block": subnet.cidr_block,
                           "available_addrs": subnet.available_ip_address_count})
        return retval

    def prepare(self):
        self.region_name = self.req.option("region")
        try:
            self.region = boto.vpc.connect_to_region(self.region_name)
        except Exception as e:
            Logger.error("VPC connection error: %s" % (e))
            self.resp.send_error("VPC connection failed")
        self.handlers["default"] = self.handle_list

    def handle_list(self):
        ids = self.req.args()
        if len(ids) == 0:
            ids = None
        elif ids[0] == "list" or ids[0] == "ls":
            ids = ids[1:]
        vpcs = []
        try:
            for vpc in self.region.get_all_vpcs(ids, filters={"state": "available"}):
                vpc_data = {"id": vpc.id,
                            "state": vpc.state,
                            "cidr_block": vpc.cidr_block,
                            "region": self.region_name}
                if self.req.option("subnets"):
                    subnets = region.get_all_subnets(filters={"vpcId": vpc.id})
                    vpc_data["subnets"] = build_subnet_list(subnets)
                vpcs.append(vpc_data)
            self.resp.append_body({"vpcs": vpc_data}, template="list_vpcs")
        except Exception as e:
            Logger.error("Error enumerating VPC data: %s" % (e))
            self.resp.send_error("VPC service error: %s" % (e))
