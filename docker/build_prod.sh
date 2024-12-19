#!/bin/bash
VERSION=2.7.9-beta
# In case of doubt on the image sanity, uncomment below
NO_CACHE=--no-cache
# Preliminary, log using ecotaxa docker account
docker login -u ecotaxa
# Copy all source files
rsync -avr --delete --exclude-from=not_to_copy.lst .. py/
# Build
docker build $NO_CACHE -t ecotaxa/ecotaxa_front -f prod_image/Dockerfile .
# Push to docker hub
docker tag ecotaxa/ecotaxa_front:latest ecotaxa/ecotaxa_front:$VERSION
docker push ecotaxa/ecotaxa_front:$VERSION
docker push ecotaxa/ecotaxa_front:latest
