from mist.commands.s3 import Base

class S3_bucket_acl(Base):

    possible_policies = ["public-read",
                         "private",
                         "public-read-write",
                         "authenticated-read"]

    def prepare(self):
        self.connect()
        self.selected_bucket = ""
        self.specified_file = ""
        self.policy = ""
        self.force = False
        # Set the args and options
        if "bucket" in self.request.options:
            self.selected_bucket = self.request.options["bucket"]
        if "file" in self.request.options:
            self.specified_file = self.request.options["file"]
        if "policy" in self.request.options:
            self.policy = self.request.options["policy"]
        if "force" in self.request.options:
            self.force = True
        buckets = self.filter_buckets(self.selected_bucket, self.get_buckets())
        self.file_keys = self.get_filtered_keys(buckets)

    def run(self):
        if self.request.args is None:
            self.usage_error()
        if self.request.args[0] == "set":
            self.handle_set()
        if self.request.args[0] == "list":
            self.handle_list()

    def get_acl(self, file_key):
        return file_key.get_acl()

    def set_acl_policies(self):
        fkey_names = ', '.join([fkey.bucket.name+":"+fkey.name for fkey in self.file_keys])
        if self.force:
            for file_key in self.file_keys:
                file_key.set_acl(self.policy)
            self.response.content({"policy": self.policy, "file_keys": fkey_names},
                                  template="set_policy").send()
        else:
            self.response.content({"policy": self.policy, "file_keys": fkey_names}, template="potential_set_policy").send()

    def package(self):
        prepared_acls = []
        for fkey in self.file_keys:
            acp = fkey.get_acl()
            prepared_acls.append({"bucket": fkey.bucket.name,
                                  "name": fkey.name,
                                  "grants": [{"name": grant.display_name,
                                              "uri": grant.uri,
                                              "permission": grant.permission,
                                              "email": grant.email_address} for grant in acp.acl.grants]})
        return prepared_acls

    def handle_list(self):
        self.response.content({"acls": self.package()}, template="list_acls").send()

    def handle_set(self):
        if self.policy.lower() in self.possible_policies:
            self.set_acl_policies()
        else:
            self.abort()
            self.response.string("Error Unknown policy. Set to one of the following: 'public-read, private, public-read-write, authenticated-read'.")

    def usage_error(self):
        self.response.abort()
        self.response.string("s3_bucket_acl [set|list] [--policy=[public-read, private, public-read-write, authenticated-read] --force] <bucket name> <filename>").send()
