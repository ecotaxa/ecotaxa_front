#
# A python generator from OpenAPI spec.
#
from os import unlink
from shutil import rmtree
from tempfile import mktemp

import requests
from datamodel_code_generator.__main__ import main as gen_main
from datamodel_code_generator.parser.jsonschema import json_schema_data_formats
from datamodel_code_generator.types import Types

# Small hack, the generator does not support 'time' type
json_schema_data_formats['string']['time'] = Types.date_time

rmtree("eco-taxa-client", ignore_errors=True)

OPENAPI_URL = "https://ecotaxa.obs-vlfr.fr/api/openapi.json"

# If in a dev environment then pick the local file
openapi_json = "../../ecotaxa_back/openapi.json"
try:
    open(openapi_json)
except FileNotFoundError:
    openapi_json = mktemp(".json")
    rsp = requests.get(OPENAPI_URL, verify=False)
    with open(openapi_json, "w") as fd:
        fd.write(rsp.text)

TEMP_GEN = "model_temp.py"
FINAL_GEN = "ecotaxa_model.py"
gen_main(["--input", openapi_json, "--output", TEMP_GEN, "--target-python-version", "3.7"])

with open(FINAL_GEN, "w") as fd_out:
    with open(TEMP_GEN) as fd_in:
        for a_line in fd_in.readlines():
            if "from __future__ import annotations" in a_line:
                continue
            fd_out.write(a_line)
unlink(TEMP_GEN)