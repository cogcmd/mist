from mist.commands.ec2 import Base

class Vpc_list(Base):
    def build_subnet_list(self, subnets):
        retval = []
        for subnet in subnets:
            retval.append({"id": subnet.id,
                           "az": subnet.availability_zone,
                           "az_default": subnet.defaultForAz,
                           "cidr_block": subnet.cidr_block,
                           "available_addrs": subnet.available_ip_address_count})
        return retval

    def run(self):
        ids = None
        if self.request.args is not None:
            ids = self.request.args
        vpcs = []
        try:
            for vpc in self.region.get_all_vpcs(ids, filters={"state": "available"}):
                vpc_data = {"id": vpc.id,
                            "state": vpc.state,
                            "cidr_block": vpc.cidr_block,
                            "region": self.region_name}
                if "subnets" in self.request.options:
                    subnets = region.get_all_subnets(filters={"vpcId": vpc.id})
                    vpc_data["subnets"] = build_subnet_list(subnets)
                vpcs.append(vpc_data)
            self.response.content({"vpcs": vpc_data}, template="list_vpcs").send()
        except Exception as e:
            self.abort()
            self.response.string("VPC service error: %s" % (e)).send()
