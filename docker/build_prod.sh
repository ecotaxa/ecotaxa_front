#!/bin/bash
VERSION=v2.7.9.3-beta
# In case of doubt on the image sanity, uncomment below
#NO_CACHE=--no-cache
# Preliminary, log using ecotaxa docker account
#docker login -u ecotaxa
# Copy all and only source files
(cd .. && git status --porcelain | grep "^??" | sed -e "s/?? //g" > docker/not_in_git.lst)
rsync -avr --delete --exclude-from=not_to_copy.lst --exclude-from=not_in_git.lst --delete-excluded .. py/
mkdir -p py/docker/prod_image
rsync -avr prod_image/*.sh prod_image/*.ini py/docker/prod_image/
# Build
docker build $NO_CACHE -t ecotaxa/ecotaxa_front -f prod_image/Dockerfile .
# Push to docker hub
docker tag ecotaxa/ecotaxa_front:latest ecotaxa/ecotaxa_front:$VERSION
#docker push ecotaxa/ecotaxa_front:$VERSION
#docker push ecotaxa/ecotaxa_front:latest
