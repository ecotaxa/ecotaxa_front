#!/bin/bash
VERSION=2.6.3
# In case of doubt on the image sanity, uncomment below
# NO_CACHE=--no-cache
# Preliminary, log using ecotaxa docker account
#docker login -u ecotaxa
# Copy all source files
rsync -avr --delete --exclude-from=not_to_copy.lst .. py/
# Build
docker build $NO_CACHE -t ecotaxa/ecotaxafront -f prod_image/Dockerfile .
# Push to docker hub
#docker tag ecotaxa/ecotaxafront:latest ecotaxa/ecotaxafront:$VERSION
#docker push ecotaxa/ecotaxafront:$VERSION
