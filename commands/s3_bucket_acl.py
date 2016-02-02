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

def get_acl(file_key):
    return file_key.get_acl()

def filter_buckets(filter_name, buckets):
    pattern = re.compile(filter_name)
    return [bucket for bucket in buckets if pattern.match(bucket.name)]

def get_filtered_keys(filter_path, buckets):
    bucket_file_keys = []
    for bucket in buckets:
        bucket_file_keys += get_filekeys(bucket)
    return [file_key for file_key in bucket_file_keys if path_match(filter_path, file_key)]

def path_match(filter_path, file_key):
    match = False
    if (file_key.path and filter_path in file_key.path) or \
       (file_key.name and filter_path in file_key.name):
        match = True
    return match

def set_acl_policies(policy, file_keys, bucketname, specified_file, force=False):
    fkey_names = ', '.join([fkey.bucket.name+":"+fkey.name for fkey in file_keys])
    if force:
        for file_key in file_keys:
            file_key.set_acl(policy)
        cog.send_text("The policy has been set to '%s' on the following: %s\n." % (policy, fkey_names))
    else:
        cog.send_text("This will set the policy to '%s' on the following: %s\nPlease pass the --force option to confirm." % (policy, fkey_names))

def respond(set_policy, file_keys, bucketname, specified_file, force=False):
    if set_policy and set_policy.lower() in ("public-read", "private", "public-read-write", "authenticated-read"):
        set_acl_policies(set_policy, file_keys, bucketname, specified_file, force)
    elif set_policy:
        cog.send_text("Error Unknown policy. Please set to one of the following: 'public-read, private, public-read-write, authenticated-read'")
    else:
        cog.send_json(prepare(file_keys))

def prepare(file_keys):
    prepared_acls = []
    for fkey in file_keys:
        acp = fkey.get_acl()
        prepared_acls.append({"bucket": fkey.bucket.name,
                              "name": fkey.name,
                              "grants": [{"name": grant.display_name, "uri": grant.uri, "permission": grant.permission, "email": grant.email_address} for grant in acp.acl.grants]})
    return prepared_acls

if __name__ == "__main__":
    conn = get_connection()
    bucketname = cog.get_arg(0, "")
    specified_file = cog.get_arg(1, "")

    buckets = filter_buckets(bucketname, get_buckets(conn))
    file_keys = get_filtered_keys(specified_file, buckets)
    respond(cog.get_option("set-policy"),
            file_keys,
            bucketname,
            specified_file,
            cog.get_option("force"))
