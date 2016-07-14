from mist.commands.s3 import Base

class S3_bucket_files(Base):

    def prepare(self):
        self.connect()
        self.selected_bucket = ""
        self.specified_filed = ""
        self.force = False

        # Set the args and options
        if "bucket" in self.request.options:
            self.selected_bucket = self.request.options["bucket"]
        if "file" in self.request.options:
            self.specified_file = self.request.options["file"]
        if "force" in self.request.options:
            self.force = True
        buckets = self.filter_buckets(self.get_buckets())
        self.file_keys = self.get_filtered_keys(buckets)

    def run(self):
        if self.request.args is None or len(self.request.args) < 1:
            self.usage_error()
        if self.request.args[0] == "delete":
            self.handle_delete(self.request.args[1:])
        elif self.request.args[0] == "list":
            self.handle_list(self.request.args[1:])
        self.usage_error()

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
            self.response.content({"file_keys": file_keynames}, template="potential_delete_bucket_files").send()
        elif self.force and self.delete_filekeys():
            self.response.content({"file_keys": file_keynames}, template="delete_bucket_files").send()
        else:
            self.abort()
            self.response.string("Error deleting file keys").send()

    def package(self):
        return [{"name": file_key.name,
                 "bucket": file_key.bucket.name} for file_key in self.file_keys]

    def handle_list(self):
        self.response.content({"file_paths": self.package()}, template="list_bucket_files").send()

    def usage_error(self):
        self.response.abort()
        self.response.string("s3_bucket_files [delete|list] [--force] --bucket=<bucket name> --file=<filename>").send()
