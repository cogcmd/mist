import re

import boto.ec2
from cog.logger import Logger
from cog.command import Command

class EC2Command(Command):

    def connect(self):
        self.region_name = self.req.option("region")
        try:
            self.region = boto.ec2.connect_to_region(self.region_name)
        except Exception as e:
            Logger.error("Error connecting to EC2: %s" % (e))
            self.resp.send_error("Cannot connect to EC2")
        if not self.region:
            Logger.error("Error: Unknown region: %s" % (self.region_name))
            self.resp.send_error("Sorry. The region '%s' is unknown." % (self.region_name))
