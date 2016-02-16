import boto.ec2

from cog.logger import Logger
from cog.command import Command

class ListKeypairsCommand(Command):
    def list_keypairs(self):
        keypairs = []
        names = self.req.args()
        if len(names) == 0:
            names = None
        for kp in self.region.get_all_key_pairs(names):
            keypairs.append({"name": kp.name,
                             "region": self.region_name,
                             "fingerprint": kp.fingerprint})
        if len(keypairs) == 0:
            self.resp.append_body([], template="empty_result")
        else:
            self.resp.append_body({"keypairs": keypairs}, template="list_keypairs")

    def prepare(self):
        self.region_name = self.req.option("region")
        try:
            self.region = boto.ec2.connect_to_region(self.region_name)
        except Exception as e:
            Logger.error("Error connecting to EC2: %s" % (e))
            self.resp.send_error("Cannot connect to EC2")
        self.handlers["default"] = self.list_keypairs

    def usage_error(self):
        self.resp.send_error("keypairs-list --region=<region_name> ...")
