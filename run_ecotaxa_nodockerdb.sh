#!/bin/bash
#
# start docker ecotaxa_db
# start ecotaxa_back
# start ecotaxa_front
gnome-terminal -- /bin/bash -c 'source venv/bin/activate && python3 runserver.py'
cd /home/imev/ecotaxa/ecotaxa_dev_current/ecotaxa_back
cd py
source venv/bin/activate
python run.py uvicorn
