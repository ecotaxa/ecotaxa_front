#!/bin/bash
# Prepare a clean source tree in ./py/ for building the production Docker image.
set -euo pipefail
# Generate list of untracked files to exclude from rsync
(cd .. && git status --porcelain --ignored | grep -e "^??" -e "^!!" | sed -e "s/.. //g" > docker/not_in_git.lst || true)
# Sync repository (parent dir) into docker/py, excluding unwanted and untracked files
rsync -avr \
  --delete \
  --exclude=docker \
  --exclude-from=not_to_copy.lst \
  --exclude-from=not_in_git.lst \
  --delete-excluded \
  .. py/
cp -ar ../docker/prod_image/*.* py
echo "Clean build source prepared in docker/py"
