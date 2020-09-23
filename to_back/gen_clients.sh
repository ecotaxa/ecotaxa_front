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
docker run --rm --network="host" -v ${PWD}/..:/client openapitools/openapi-generator-cli:v4.3.1 generate \
 -i ${SRC} -g python \
 --minimal-update \
 --additional-properties=generateSourceCodeOnly=true,packageName=to_back.ecotaxa_cli_py \
 -o /client
 # Linux: Generated files belong to root, fix it.
 sudo chown -R $(id -u):$(id -g) ${PWD}