#!/bin/bash
#
# start docker ecotaxa_db
# start ecotaxa_back
# start ecotaxa_front
DB=""
DEV_BACK="../ecotaxa_back"
while getopts "B:P:" flag
   do
     case "${flag}" in
       B) DB=${OPTARG};;
       P) DEV_BACK=${OPTARG};;
      esac
done

gnome-terminal -- /bin/bash -c 'source venv/bin/activate && python3 runserver.py'
cd $DEV_BACK
docker stop ecotaxa_db
if [ "$DB" == docker ]
then
  echo "DB: $DB  ----- ecotaxa_db docker db running";
  docker start ecotaxa_db
else
  echo "db server"
fi
cd py
source venv/bin/activate
python3.8 run.py uvicorn
