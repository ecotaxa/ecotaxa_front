#!/bin/bash
#
# start docker ecotaxa_db
# start ecotaxa_back
# start ecotaxa_front
gnome-terminal -- /bin/bash -c 'source venv/bin/activate && python3 runserver.py'
cd /home/imev/ecotaxa/ecotaxa_dev_current/ecotaxa_back
docker stop ecotaxa_db
docker start ecotaxa_db
cd py
source venv/bin/activate
python3.8 run.py uvicorn
