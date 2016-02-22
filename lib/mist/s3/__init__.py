import re

from boto.s3.connection import S3Connection
from cog.logger import Logger
from cog.command import Command

class S3Command(Command):

    def connect(self):
        try:
            self.conn = S3Connection()
        except Exception as e:
            Logger.error("Failed connecting to S3: %s" % (e))
            self.resp.send_error("S3 connection failed.")

    def get_buckets(self):
        return self.conn.get_all_buckets()

    def get_filekeys(self, bucket):
        return bucket.get_all_keys()

    def filter_buckets(self, buckets):
        pattern = re.compile(self.selected_bucket)
        return [bucket for bucket in buckets if pattern.match(bucket.name)]

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

    def path_match(self, file_key):
        match = False
        if (file_key.path and self.specified_file in file_key.path) or \
           (file_key.name and self.specified_file in file_key.name):
            match = True
        return match

    def get_filtered_keys(self, buckets):
        bucket_file_keys = []
        for bucket in buckets:
            bucket_file_keys += self.get_filekeys(bucket)
        return [file_key for file_key in bucket_file_keys if self.path_match(file_key)]

