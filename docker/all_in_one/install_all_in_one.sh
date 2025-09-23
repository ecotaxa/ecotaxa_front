#!/bin/sh
docker stop portable_ecotaxafront
docker stop portable_ecotaxaback
docker stop portable_ecotaxagpuback
docker rm portable_ecotaxafront
docker rm portable_ecotaxaback
docker rm portable_ecotaxagpuback
docker rmi ecotaxa/ecotaxa_front:latest
docker rmi ecotaxa/ecotaxa_back:latest
docker rmi ecotaxa/ecotaxa_gpu_back:latest
docker compose -f docker-compose.yml -p portable up -d  &&
sleep 5s &&
docker exec -i portable_pgdb_1 psql -U postgres -h localhost -c "create DATABASE ecotaxa WITH OWNER=postgres ENCODING='UTF8' TEMPLATE=template0 LC_CTYPE='C' LC_COLLATE='C' CONNECTION LIMIT=-1;" &&
docker start portable_ecotaxaback  &&
#docker exec -i portable_ecotaxaback bash -c "PYTHONPATH=. python cmds/manage.py db create --password mysecretpassword --db-name ecotaxa" &&
echo " db created" &&
docker exec -i portable_ecotaxaback bash -c "PYTHONPATH=. python cmds/manage.py db build" &&
#replace adminstrator by a "valid" email
docker exec -i portable_pgdb_1 psql -U postgres -h localhost -d ecotaxa -c "UPDATE users SET email='administrator@mail.test' WHERE id=1;"  &&
echo "connect with administrator@mail.test" &&
docker stop portable_ecotaxaback &&
echo " end install" &&
docker compose  -f docker-compose.yml -p portable up &&
echo "http://localhost:8088"