from mist.commands.ec2 import Base

class Keypairs_list(Base):
    def run(self):
        self.connect()
        keypairs = []
        names = self.request.args
        for kp in self.region.get_all_key_pairs(names):
            keypairs.append({"name": kp.name,
                             "region": self.region_name,
                             "fingerprint": kp.fingerprint})
        if len(keypairs) == 0:
            self.response.content([], template="empty_result").send()
        else:
            self.response.content({"keypairs": keypairs}, template="list_keypairs").send()
