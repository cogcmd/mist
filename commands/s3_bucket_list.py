#!/usr/bin/env python

import re
import os
import mist.cog as cog
from boto.s3.connection import S3Connection

def get_connection():
    return S3Connection()

def get_buckets(conn):
    return conn.get_all_buckets()

def get_filekeys(bucket):
    return bucket.get_all_keys()

def filter_buckets(filter_name, buckets):
    pattern = re.compile(filter_name)
    return [bucket for bucket in buckets if pattern.match(bucket.name)]

def path_match(filter_path, file_key):
    match = False
    if (file_key.path and filter_path in file_key.path) or \
       (file_key.name and filter_path in file_key.name):
        match = True
    return match

def get_filtered_keys(filter_path, buckets):
    bucket_file_keys = []
    for bucket in buckets:
        bucket_file_keys += get_filekeys(bucket)
    return [file_key for file_key in bucket_file_keys if path_match(filter_path, file_key)]

def delete_filekeys(file_keys):
    try:
        for file_key in file_keys:
            file_key.delete()
    except:
        return False
    else:
        return True

def respond(file_keys, delete = False, force = False):
    if delete and force:
        if delete_filekeys(file_keys):
            cog.send_json(prepare(file_keys))
        else:
            cog.send_error("Error deleting file keys")
    elif delete:
        file_keynames = ', '.join([file_key.bucket.name+':'+file_key.name for file_key in file_keys])
        response = "This will delete the following files: %s\nPlease pass the --force option to confirm." % (file_keynames)
        cog.send_json({"body": response})
    else:
        cog.send_json(prepare(file_keys))


def prepare(file_keys):
    return [{"name": file_key.name, "bucket": file_key.bucket.name} for file_key in file_keys]

if __name__ == "__main__":
    conn = get_connection()
    buckets = filter_buckets(cog.get_arg(0, ""), get_buckets(conn))
    file_keys = get_filtered_keys(cog.get_arg(1, ""), buckets)
    respond(file_keys, cog.get_option("delete"), cog.get_option("force"))
