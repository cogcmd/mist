def kv_tag_parse(tags):
    parsed = {}
    if tags is not None:
        pairs = tags.split(",")
        for pair in pairs:
            kv = pair.split("=")
            if len(parsed) == 2:
                parsed[kv[0]] = kv[1]
            else:
                parsed[kv[0]] = ""
    return parsed
