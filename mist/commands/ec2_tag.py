from mist.commands.ec2 import Base
import mist.commands.util

class TagCommand(Base):
    def handle_add(self):
        for instance in self.region.get_only_instances(instance_ids=self.instances):
            instance.add_tags(self.parsed_tags)
        self.response.content({"instances": self.instances,
                               "region": self.region,
                               "tags": self.request.options["tags"],
                               "action": "added"}, template="update_tags").send()
    def handle_remove(self):
        for instance in self.region_get_only_instances(instance_ids=self.instances):
            instance.remove_tags(self.parsed_tags)
        self.response.content({"instances": self.instances,
                               "region": self.region,
                               "tags": self.orig_tags,
                               "action": "removed"}, template="update_tags").send()

    def usage_error(self):
        self.response.abort()
        self.response.string("ec2_tags --region=<region> --tags=<tags> [add|remove|rm] instance1 ...").send()

    def run(self):
        if self.request.args == None or len(self.request.args) < 2:
            self.usage_error()
        self.instances = self.request.args[1:]
        self.parsed_tags = util.kv_tag_parse(self.request.options["tags"])
        self.connect()
        if self.request.args[0] == "add":
            self.handle_add()
        elif self.request.args[0] == "remove":
            self.handle_remove()
        elif self.request.args[0] == "rm":
            self.handle_remove()
        else:
            self.usage_error()

