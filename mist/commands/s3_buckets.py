import re

from mist.commands.s3 import Base
from boto.exception import S3CreateError

class S3_buckets(Base):

    def run(self):
        self.connect()
        if self.request.args is not None:
            if self.request.args[0] == "list":
                self.handle_list(self.request.args[1:])
            elif self.request.args[0] == "delete":
                self.handle_delete(self.request.args[1:])
            elif self.request.args[0] == "create":
                self.handle_create(self.request.args[1:])
        self.usage_error()

    def handle_list(self, args):
        if len(args) == 0:
            args = [".*"]
        try:
            patterns = [re.compile(arg) for arg in args]
            buckets = [{"bucket": bucket.name} for bucket in self.find_matching(patterns)]
            if len(buckets) == 0:
                self.response.content([], template="empty_result").send()
            else:
                self.response.content({"buckets": buckets}, template="list_buckets").send()
        except Exception as e:
            Logger.error("Regex compilation error: %s" % (e))
            self.abort()
            self.response.string("Invalid regular expression: '%s'" % (self.req.arg(0))).send()

    def usage_error(self):
        self.abort()
        self.response.string("s3_buckets [list|delete|create] ...").send()

    def handle_delete(self, args):
        if len(args) == 0:
            self.usage_error()
        try:
            patterns = [re.compile(arg) for arg in args[1:]]
            buckets = self.find_matching(patterns)
            try:
                for bucket in buckets:
                    bucket.delete()
            except Exception as e:
                bucketnames = [bucket.name for bucket in buckets]
                self.abort()
                self.response.string("Error deleting buckets '%s': %s" % (bucketnames, e)).send()
            if len(buckets) == 0:
                self.response.content([], template="empty_result").send()
            else:
                bucket_names = [bucket.name for bucket in buckets]
                self.response.content({"buckets": bucket_names}, template="delete_buckets").send()
        except Exception as e:
            self.abort()
            self.response.content("One of the following regular expressions is invalid: %s, %s" % (args[1:], e)).send()

    def handle_create(self, args):
        if len(args) < 1:
            self.usage_error()
        errors = []
        for bucketname in args:
            try:
                bucket = self.conn.create_bucket(bucketname)
            except S3CreateError:
                errors.append(bucketname)
            except Exception as e:
                self.response.abort()
                self.response.string("There was a problem creating the S3 bucket(s): %s" % (e)).send()
        if len(errors) == 1:
            self.response.abort()
            self.response.string("The bucket name `%s` is not a unique name. Please choose a different name." % (errors[0])).send()
        elif len(errors) > 1:
            self.response.abort()
            self.response.string("The bucket names: `%s` are not unique names. Please choose different names." % (", ".join(errors))).send()
        else:
            self.response.content({"buckets": buckets}, template="create_buckets").send()
