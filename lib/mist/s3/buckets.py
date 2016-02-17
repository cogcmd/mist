import re

from boto.s3.connection import S3Connection
from cog.logger import Logger
from cog.command import Command

class ListBucketsCommand(Command):

    def name_matches(self, name, patterns):
        for pattern in patterns:
            if pattern.match(name):
                return True
        return False

    def find_matching(self, patterns):
        try:
            return [bucket for bucket in self.conn.get_all_buckets() if self.name_matches(bucket.name, patterns)]
        except Exception as e:
            Logger.error("S3 error: %s" % (e))
            self.resp.send_error("S3 error")

    def handle_list(self):
        args = [".*"]
        if self.req.arg_count() > 0:
            args = self.req.args()
        else:
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
            bucket_names = [{"bucket": bucket.name} for bucket in buckets]
            try:
                while len(buckets) > 0:
                    bucket = buckets[0]
                    bucket.delete()
                    buckets = buckets[1:]
            except Exception as e:
                Logger.error("Error deleting S3 bucket '%s': %s" & (buckets[0].name, e))
                self.resp.send_error("Error deleting bucket '%s': %s" % (buckets[0].name, e))
            if len(buckets) == 0:
                self.resp.append_body([], template="empty_result")
            else:
                self.resp.append_body({"buckets": buckets}, template="delete_buckets")
        except Exception as e:
            self.resp.send_error("One of the following regular expressions is invalid: %s" % (args[1:]))

    def prepare(self):
        try:
            self.conn = S3Connection()
        except Exception as e:
            Logger.error("Failed connecting to S3: %s" % (e))
            self.resp.send_error("S3 connection failed.")
        self.handlers["default"] = self.handle_list

    def usage_error(self):
        self.resp.send_error("s3-buckets [list|rm|delete|new] ...")
