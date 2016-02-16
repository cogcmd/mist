import boto.ec2

import json
from cog.logger import Logger
from cog.command import Command

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
            filters["instance-state-name"] = cog.get_option("state")
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
