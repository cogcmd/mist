import re

from cog.logger import Logger
from mist.s3 import S3Command
from boto.exception import S3CreateError

class ListBucketsCommand(S3Command):

    def prepare(self):
        self.connect()
        self.handlers["default"] = self.handle_list

    def usage_error(self):
        self.resp.send_error("s3-buckets [list|rm|delete|new] ...")

    def handle_list(self):
        args = [".*"]
        if self.req.arg_count() > 0:
            args = self.req.args()
        try:
            patterns = [re.compile(arg) for arg in args]
            buckets = [{"bucket": bucket.name} for bucket in self.find_matching(patterns)]
            if len(buckets) == 0:
                self.resp.append_body([], template="empty_result")
            else:
                self.resp.append_body({"buckets": buckets}, template="list_buckets")
        except Exception as e:
            Logger.error("Regex compilation error: %s" % (e))
            self.resp.send_error("Invalid regular expression: '%s'" % (self.req.arg(0)))

    def handle_rm(self):
        self.handle_delete()

    def handle_delete(self):
        if self.req.arg_count() < 2:
            self.usage_error()
        args = self.req.args()
        try:
            patterns = [re.compile(arg) for arg in args[1:]]
            buckets = self.find_matching(patterns)
            try:
                for bucket in buckets:
                    bucket.delete()
            except Exception as e:
                bucketnames = [bucket.name for bucket in buckets]
                Logger.error("Error deleting S3 buckets (%s): %s" % (bucketnames, e))
                self.resp.send_error("Error deleting buckets '%s': %s" % (bucketnames, e))
            if len(buckets) == 0:
                self.resp.append_body([], template="empty_result")
            else:
                bucket_names = [bucket.name for bucket in buckets]
                self.resp.append_body({"buckets": bucket_names}, template="delete_buckets")
        except Exception as e:
            self.resp.send_error("One of the following regular expressions is invalid: %s, %s" % (args[1:], e))

    def handle_create(self):
        self.handle_new()

    def handle_new(self):
        if self.req.arg_count() < 2:
            self.usage_error()
        buckets = self.req.args()[1:]
        errors = []
        for bucketname in buckets:
            try:
                bucket = self.conn.create_bucket(bucketname)
            except S3CreateError:
                errors.append(bucketname)
            except Exception as e:
                self.resp.send_error("There was a problem creating the S3 bucket(s): %s" % (e))
        if len(errors) == 1:
            self.resp.send_error("The bucket name `%s` is not a unique name. Please choose a different name." % (errors[0]))
        elif len(errors) > 1:
            self.resp.send_error("The bucket names: `%s` are not unique names. Please choose different names." % (", ".join(errors)))
        else:
            self.resp.append_body({"buckets": buckets}, template="create_buckets")


class BucketAclCommand(S3Command):

    possible_policies = ["public-read",
                         "private",
                         "public-read-write",
                         "authenticated-read"]

    def prepare(self):
        self.connect()

        # Set the args and options
        self.selected_bucket = self.req.option("bucket") or ""
        self.specified_file = self.req.option("file") or ""
        self.policy = self.req.option("policy") or ""
        self.force = self.req.option("force") or False

        buckets = self.filter_buckets(self.selected_bucket, self.get_buckets())
        self.file_keys = self.get_filtered_keys(buckets)

        self.handlers["default"] = self.handle_list

    def get_acl(self, file_key):
        return file_key.get_acl()

    def set_acl_policies(self):
        fkey_names = ', '.join([fkey.bucket.name+":"+fkey.name for fkey in self.file_keys])
        if self.force:
            for file_key in self.file_keys:
                file_key.set_acl(self.policy)
            self.resp.append_body({"policy": self.policy, "file_keys": fkey_names},
                                  template="set_policy")
        else:
            self.resp.append_body({"policy": self.policy, "file_keys": fkey_names}, template="potential_set_policy")

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
        self.resp.append_body({"acls": self.package()}, template="list_acls")

    def handle_set(self):
        if self.policy.lower() in self.possible_policies:
            self.set_acl_policies()
        else:
            self.resp.send_error("Error Unknown policy. Set to one of the following: 'public-read, private, public-read-write, authenticated-read'.")

    def usage_error(self):
        self.resp.send_error("s3-bucket-acl [set|list] [--policy=[public-read, private, public-read-write, authenticated-read] --force] <bucket name> <filename>")


class BucketFileCommand(S3Command):

    def prepare(self):
        self.connect()

        # Set the args and options
        self.selected_bucket = self.req.option("bucket") or ""
        self.specified_file = self.req.option("file") or ""
        self.force = self.req.option("force") or False

        buckets = self.filter_buckets(self.get_buckets())
        self.file_keys = self.get_filtered_keys(buckets)

        self.handlers["default"] = self.handle_list

    def delete_filekeys(self):
        try:
            for file_key in self.file_keys:
                file_key.delete()
        except:
            return False
        else:
            return True

    def handle_delete(self):
        file_keynames = ', '.join([file_key.bucket.name+':'+file_key.name for file_key in self.file_keys])
        if not self.force:
            self.resp.append_body({"file_keys": file_keynames}, template="potential_delete_bucket_files")
        elif self.force and self.delete_filekeys():
            self.resp.append_body({"file_keys": file_keynames}, template="delete_bucket_files")
        else:
            self.resp.send_error("Error deleting file keys")

    def package(self):
        return [{"name": file_key.name,
                 "bucket": file_key.bucket.name} for file_key in self.file_keys]

    def handle_list(self):
        self.resp.append_body({"file_paths": self.package()}, template="list_bucket_files")

    def usage_error(self):
        self.resp.send_error("s3-bucket-files [delete|list] [--force] --bucket=<bucket name> --file=<filename>")
