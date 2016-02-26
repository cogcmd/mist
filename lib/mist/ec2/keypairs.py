from cog.logger import Logger
from mist.ec2 import EC2Command

class ListKeypairsCommand(EC2Command):
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
        self.connect()
        self.handlers["default"] = self.list_keypairs

    def usage_error(self):
        self.resp.send_error("keypairs-list --region=<region_name> ...")
