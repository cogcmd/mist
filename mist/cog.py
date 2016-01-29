import json
import string
import os

def send_json(data):
    print "JSON\n"
    print "%s\n" % (json.dumps(data))

def name_to_option_var(name):
    return "COG_OPT_" + string.upper(name)

def index_to_arg_var(index):
    return "COG_ARG_" + str(index)

def has_option(name):
    var_name = name_to_option_var(name)
    return os.getenv(var_name) is not None

def get_option(name):
    var_name = name_to_option_var(name)
    return os.getenv(var_name)

def get_arg_count():
    arg_count = os.getenv("COG_ARGC")
    if arg_count is None:
        return 0
    else:
        return int(arg_count)

def get_arg(index):
    arg_var = index_to_arg_var(index)
    return os.getenv(arg_var)