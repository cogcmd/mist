from cog.command import Command
import boto.ec2

class Base(Command):
    def __init__(self):
        super().__init__()
        self.region = None

    def connect(self):
        self.region = boto.ec2.connect_to_region(self.request.options["region"])

