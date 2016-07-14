from mist.commands.ec2 import Base
import mist.commands.util

class Ec2_create(Base):
    def tag_instances(self, instance_ids, tags):
        instances = self.region.get_only_instances(instance_ids = instance_ids)
        for instance in instances:
            instance.add_tags(tags)

    def prepare(self):
        self.az = None
        self.subnet = None
        self.user_data = None
        self.tags = None
        self.instance_type = self.request.options["type"]
        self.ami = self.request.options["ami"]
        self.keypair = self.request.options["keypair"]
        if "az" in self.request.options:
            self.az = self.request.options["az"]
        if "subnet" in self.request.options:
            self.subnet = self.request.options["subnet"]
        if "user-data" in self.request.options:
            self.user_data = self.request.options["user-data"]
        if "tags" in self.request.options:
            self.tags = util.kv_tag_parse(self.request.options["tags"])

    def run(self):
        self.connect()
        count = 1
        if self.request.args is not None:
            try:
                count = int(self.request.args[0])
            except:
                self.response.abort()
                self.response.string("Sorry. I don't know how to turn '%s' into a number." % (self.request.args[0])).send()
        try:
            reservation = self.region.run_instances(self.ami, min_count=count, max_count=count, instance_type=self.instance_type,
                                                    placement=self.az, key_name=self.keypair, subnet_id=self.subnet,
                                                    user_data=self.user_data)
            instance_ids = [instance.id for instance in reservation.instances]
            if self.tags is not None:
                tag_instances(instance_ids, tags)
            self.response.content({"instances": instance_ids}, template="create_instances").send()
        except Exception as e:
            self.response.abort()
            self.response.string("Error creating instances: %s" % (e))
