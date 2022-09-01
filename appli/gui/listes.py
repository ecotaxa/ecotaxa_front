from typing import List
from os import path


def list_json_data(name="sponsors") -> List:
    import json

    jsondata = {}
    jsondata[name] = []
    jsonfile = "appli/static/gui/json/" + name + ".json"
    if path.exists(jsonfile):
        with open(jsonfile, encoding="utf-8") as file:
            jsondata = json.load(file)
    return jsondata[name]
