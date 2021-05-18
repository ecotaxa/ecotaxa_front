#!/bin/bash
#
# Generate client stubs for python
#
# Fetches the API definition from GitHub or local directory for faster development cycle.
#
rm -rf ecotaxa_cli_py
SRC="https://raw.githubusercontent.com/ecotaxa/ecotaxa_back/master/openapi.json"
if test -f "openapi.json"; then
  # A bit disturbing, but it's the same file, openapi.json in current directory is in /client as seen from docker
  SRC="/client/to_back/openapi.json"
fi
# openapi generator removed any python typings or just auto-completion hints in 5.1.1,
# so the main point of generators is a bit lost to me.
docker run --rm --network="host" -v ${PWD}/..:/client -u $(id -u ${USER}):$(id -g ${USER}) \
 openapitools/openapi-generator-cli:v4.3.1 generate \
 -i ${SRC} -g python \
 --minimal-update \
 --additional-properties=generateSourceCodeOnly=true,packageName=to_back.ecotaxa_cli_py \
 -o /client
# Remove the _api_ in defs which come from leading /api in URLs
#for f in ecotaxa_cli_py/api/*.py
#do
#  sed -i 's/_api_/_/g' $f
#done