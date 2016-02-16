#!/usr/bin/env python

import re
import os
import mist.cog as cog
from boto.s3.connection import S3Connection

def get_connection():
    return S3Connection()

def get_buckets(conn):
    return conn.get_all_buckets()

def filter_buckets(filter_string, buckets):
    pattern = re.compile(filter_string)
    return [bucket for bucket in buckets if pattern.match(bucket.name)]

def delete_buckets(buckets):
    try:
        for bucket in buckets:
            bucket.delete()
    except:
        return False
    else:
        return True

def respond(buckets, delete = False, force = False):
    if delete and force:
        if delete_buckets(buckets):
            cog.send_json(prepare(buckets))
        else:
            cog.send_error("Error deleting buckets")
    elif delete:
        bucket_names = ', '.join([bucket.name for bucket in buckets])
        response = "This will delete the following buckets: %s\nPlease pass the --force option to confirm." % bucket_names
        cog.send_json({"body": response})
    else:
        cog.send_json(prepare(buckets))


def prepare(buckets):
    return [{"name": bucket.name} for bucket in buckets]

if __name__ == "__main__":
    conn = get_connection()
    buckets = filter_buckets(cog.get_arg(0, ""), get_buckets(conn))
    respond(buckets, cog.get_option("delete"), cog.get_option("force"))
