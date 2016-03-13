#!/usr/bin/env python

import yaml
import sys

if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        try:
            contents = f.read()
            yaml.load(contents)
            print "config.yaml validated successfully."
        except ValueError as e:
            print "config.yaml failed validation: %s" % (e.message)
            sys.exit(2)

