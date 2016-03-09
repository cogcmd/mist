# Mist - AWS Bundle for Cog

## What's included?

Mist uses python's `boto` library to run a suite of commands.

```
mist:ec2-create
mist:ec2-destroy
mist:ec2-find
mist:ec2-reboot
mist:ec2-start
mist:ec2-stop
mist:ec2-tag
mist:keypairs-list
mist:s3-bucket-acl
mist:s3-bucket-list
mist:s3-buckets
mist:vpc-list
```

We also include some fine-grained permissions to control access to these
commands.

```
mist:view
mist:change-state
mist:destroy
mist:create
mist:manage-tags
mist:change-acl
```

## Building

To build the bundle you will need python, pip and PyYAML installed. Then just run the following:

```
make
```

This should create a `mist.cog` file in the current directory.

## Installing and Configuring

You'll need to have `python` and `pip` available before installing.

To install the bundle, copy this file to Relay's `pending/` directory.

Once it's installed, you'll need to add your AWS credentials to `config.json`
in the `COG_COMMAND_CONFIG_ROOT/mist` directory.

Here's an example `config.json`:

```
{"AWS_ACCESS_KEY_ID": "ABCDEFGHIJKLMNOPQRST",
 "AWS_SECRET_ACCESS_KEY": "U/nV0+l/Some0Obvious1Fake2Key3For4AWS5"}
```
