from mist.commands.ec2 import Base

class Ec2_find(Base):
    def update_dict(self, data, key, value):
        if key in data:
            existing = data[key]
            data[key] = existing.append(value)
        else:
            data[key] = [value]
        return data

    def parse_tags(self, filters):
        tags = self.request.options["tags"]
        if tags is not None:
            pairs = tags.split(",")
            for pair in pairs:
                parsed = pair.split("=")
                if len(parsed) == 2:
                    key = "tag:" + parsed[0]
                    self.update_dict(filters, key, parsed[1])
                elif parsed[0] == "":
                    self.update_dict(filters, "tag-value", parsed[1])
                else:
                    self.update_dict(filters, "tag-key", parsed[0])
        return filters

    def build_filters(self):
        filters = {}
        if "ami" in self.request.options:
            filters["image_id"] = self.request.options["ami"]
        if "state" in self.request.options:
            filters["instance-state-name"] = self.request.options["state"]
        if "tags" in self.request.options:
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
        returned_fields = self.request.options["return"]
        if returned_fields is None:
            returned_fields = "id,ami,state,privip,tags,region,az"
        self.returned_fields = []
        for field in returned_fields.split(","):
            self.returned_fields.append(field.strip())
        self.returned_fields.sort()

    def run(self):
        try:
            self.connect()
            instances = self.region.get_only_instances(filters=self.build_filters())
            if len(instances) == 0:
                self.response.content({"instances": []}, template="empty_result").send()
            else:
                formatted = self.format_results(instances)
                self.response.content(formatted).send()
        except Exception as e:
            self.response.abort()
            self.response.string("Error searching for instances: %s" % (e)).send()
