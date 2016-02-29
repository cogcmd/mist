import boto.ec2

from cog.logger import Logger
from cog.command import Command

def kv_tag_parse(tags):
    parsed = {}
    if tags is not None:
        pairs = tags.split(",")
        for pair in pairs:
            kv = pair.split("=")
            if len(parsed) == 2:
                parsed[kv[0]] = kv[1]
            else:
                parsed[kv[0]] = ""
    return parsed

class CreateCommand(Command):
    def tag_instances(self, instance_ids, tags):
        instances = self.region.get_only_instances(instance_ids = instance_ids)
        for instance in instances:
            instance.add_tags(tags)

    def create_instance(self):
        count = 1
        if self.req.arg_count() > 0:
            try:
                count = int(self.req.arg(0))
            except:
                self.resp.send_error("Sorry. I don't know how to turn '%s' into a number." % (self.req.arg(0)))
        reservation = self.region.run_instances(self.ami, min_count=count, max_count=count, instance_type=self.instance_type,
                                                placement=self.az, key_name=self.keypair, subnet_id=self.subnet,
                                                user_data=self.user_data)
        instance_ids = [instance.id for instance in reservation.instances]
        if self.tags is not None:
            tag_instances(instance_ids, tags)
        self.resp.append_body({"instances": instance_ids}, template="create_instances")

    def prepare(self):
        region_name = self.req.option("region")
        try:
            self.region = boto.ec2.connect_to_region(region_name)
        except Exception as e:
            Logger.error("Error connecting to EC2: %s" % (e))
            self.resp.send_error("Cannot connect to EC2")
        self.instance_type = self.req.option("type")
        self.ami = self.req.option("ami")
        self.keypair = self.req.option("keypair")
        self.az = self.req.option("az")
        self.subnet = self.req.option("subnet")
        self.user_data = self.req.option("user-data")
        tags = kv_tag_parse(self.req.option("tags"))
        if len(tags) > 0:
            self.tags = tags
        else:
            self.tags = None
        self.handlers["default"] = self.create_instance

    def usage_error(self):
        self.resp.send_error("ec2-create --region=<region> --type=<type> --ami=<ami> --keypair=<keypair> instance_count")


class FindCommand(Command):
    def update_dict(self, data, key, value):
        if data.has_key(key):
            existing = data[key]
            data[key] = existing.append(value)
        else:
            data[key] = [value]
        return data

    def parse_tags(self, filters):
        tags = self.req.option("tags")
        if tags is not None:
            pairs = tags.split(",")
            for pair in pairs:
                parsed = pair.split("=")
                if len(parsed) == 2:
                    key = "tag:" + parsed[0]
                    self.update_dict(filters, key, parsed[1])
                else:
                    if parsed[0] == "":
                        self.update_dict(filters, "tag-value", parsed[1])
                    else:
                        self.update_dict(filters, "tag-key", parsed[0])
        return filters

    def build_filters(self):
        filters = {}
        ami = self.req.option("ami")
        state = self.req.option("state")
        tags = self.req.option("tags")
        if ami is not None:
            filters["image_id"] = ami
        if state is not None:
            filters["instance-state-name"] = state
        filters = self.parse_tags(filters)
        return filters

    def format_results(self, instances):
        retval = []
        for instance in instances:
            di = {}
            for field in self.returned_fields:
                if field == "id":
                    di["id"] = instance.id
                elif field == "region":
                    di["region"] = self.region_name
                elif field == "pubdns":
                    di["pubdns"] = instance.public_dns_name
                elif field == "privdns":
                    di["privdns"] = instance.private_dns_name
                elif field == "state":
                    di["state"] = instance.state
                elif field == "keyname":
                    di["keyname"] = instance.key_name
                elif field == "ami":
                    di["ami"] = instance.image_id
                elif field == "kernel":
                    di["kernel"] = instance.kernel
                elif field == "arch":
                    di["arch"] = instance.architecture
                elif field == "vpc":
                    di["vpc"] = instance.vpc_id
                elif field == "pubip":
                    di["pubip"] = instance.ip_address
                elif field == "privip":
                    di["privip"] = instance.private_ip_address
                elif field == "az":
                    di["az"] = instance.placement
                elif field == "type":
                    di["type"] = instance.instance_type
                elif field == "tags":
                    di["tags"] = instance.tags
            retval.append(di)
        return retval

    def parse_returned_fields(self):
        returned_fields = self.req.option("return")
        if returned_fields is None:
            returned_fields = "id,ami,state,privip,tags,region,az"
        self.returned_fields = []
        for field in returned_fields.split(","):
            self.returned_fields.append(field.strip())
        self.returned_fields.sort()

    def find_instances(self):
        instances = self.region.get_only_instances(filters=self.build_filters())
        if len(instances) == 0:
            self.resp.append_body({"instances": []}, template="empty_result")
        else:
            formatted = self.format_results(instances)
            self.resp.append_body(formatted)

    def prepare(self):
        self.region_name = self.req.option("region")
        try:
            self.region = boto.ec2.connect_to_region(self.region_name)
        except Exception as e:
            Logger.error("Error connecting to EC2: %s" % (e))
            self.resp.send_error("Cannot connect to EC2")
        self.parse_returned_fields()
        self.handlers["default"] = self.find_instances

    def usage_error(self):
        self.send_error("ec2-find --region=<region_name> ...")


class DestroyCommand(Command):
    def prepare(self):
        self.region_name = self.req.get_option("region")
        try:
            self.region = boto.ec2.connect_to_region(region_name)
        except Exception as e:
            Logger.error("Connecting to EC2 failed: %s" % (e))
            self.resp.send_error("Connecting to EC2 failed")
        self.handlers["default"] = self.destroy_instances

    def destroy_instances(self):
        instances = self.req.args()
        if len(instances) == 0:
            self.resp.append_body([], template="empty_result")
        else:
            try:
                region.terminate_instances(instances)
                self.resp.append_body({"terminated": instances})
            except Exception as e:
                self.resp.send_error("Error during instance termination: %s" % (e))

    def usage_error(self):
        self.resp.send_error("ec2-destroy --region=<region_name> ...")


class ChangeStateCommand(Command):
    def handle_reboot(self):
        if len(self.instances) > 0:
            self.region.reboot_instances(self.instances)
        self.resp.append_body({"instances": self.instances,
                               "region": self.region_name,
                               "action": "rebooted"}, template="state_change")

    def handle_stop(self):
        if len(self.instances) > 0:
            self.region.stop_instances(self.instances)
        self.resp.append_body({"instances": self.instances,
                               "region": self.region_name,
                               "action": "stopped"}, template="state_change")

    def handle_start(self):
        if len(self.instances) > 0:
            self.region.start_instances(self.instances)
        self.resp.append_body({"instances": self.instances,
                               "region": self.region_name,
                               "action": "started"}, template="state_change")

    def prepare(self):
        self.region_name = self.req.option("region")
        try:
            self.region = boto.ec2.connect_to_region(self.region_name)
        except Exception as e:
            Logger.error("Error connecting to EC2: %s" % (e))
            self.resp.send_error("Cannot connect to EC2")
        args = self.req.args()
        if len(args) < 2:
            self.usage_error()
        else:
            self.instances = args[1:]

    def usage_error(self):
        self.resp.send_error("ec2-state [start|stop|reboot] ...")


class TagCommand(Command):
    def handle_add(self):
        for instance in self.region.get_only_instances(instance_ids=self.instances):
            instance.add_tags(self.tags)
        self.resp.append_body({"instances": self.instances,
                             "region": self.region,
                             "tags": self.orig_tags,
                             "action": "added"}, template="update_tags")
    def handle_remove(self):
        for instance in self.region_get_only_instances(instance_ids=self.instances):
            instance.remove_tags(self.tags)
        self.resp.append_body({"instances": self.instances,
                             "region": self.region,
                             "tags": self.orig_tags,
                             "action": "removed"}, template="update_tags")

    def handle_rm(self):
        self.handle_remove()

    def prepare(self):
        if self.req.arg_count() < 2:
            self.usage_error()
        args = self.req.args()
        self.instances = args[1:]
        self.region_name = self.req.option("region")
        try:
            self.region = boto.ec2.connect_to_region(self.region_name)
        except Exception as e:
            Logger.error("Error connecting to EC2: %s" % (e))
            self.resp.send_error("Cannot connect to EC2")
        self.orig_tags = self.req.option("tags")
        self.tags = kv_tag_parse(self.req.option("tags"))

    def usage_error(self):
        self.resp.send_error("ec2-tags --region=<region> --tags=<tags> [add|remove|rm] ...")
