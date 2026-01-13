#!/bin/bash
VERSION=3.0.0
# In case of doubt on the image sanity, uncomment below
#NO_CACHE=--no-cache
# Preliminary, log using ecotaxa docker account
#docker login -u ecotaxa
# Prepare clean source tree for build context
bash build_clean_src.sh
# Build
docker build $NO_CACHE -t ecotaxa/ecotaxa_front -f prod_image/Dockerfile .
# Push to docker hub
docker tag ecotaxa/ecotaxa_front:latest ecotaxa/ecotaxa_front:$VERSION
docker push ecotaxa/ecotaxa_front:$VERSION
docker push ecotaxa/ecotaxa_front:latest
