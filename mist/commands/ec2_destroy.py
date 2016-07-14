from mist.commands.ec2 import Base

class Ec2_destroy(Base):
    def run(self):
        self.connect()
        instances = self.request.args()
        if len(instances) == 0:
            self.response.content([], template="empty_result").send()
        else:
            try:
                self.region.terminate_instances(instances)
                self.response.content({"terminated": instances}).send()
            except Exception as e:
                self.response.abort()
                self.response.string("Error during instance termination: %s" % (e)).send()
