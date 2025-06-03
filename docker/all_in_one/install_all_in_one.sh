#!/bin/sh
docker-compose -p portable up -d  &&
sleep 5s &&
docker exec -i portable_pgdb_1 psql -U postgres -h localhost -c "create DATABASE ecotaxa WITH OWNER=postgres ENCODING='UTF8' TEMPLATE=template0 LC_CTYPE='C' LC_COLLATE='C' CONNECTION LIMIT=-1;" &&
docker start portable_ecotaxaback_1  &&
#docker exec -i portable_ecotaxaback_1 bash -c "PYTHONPATH=. python cmds/manage.py db create --password mysecretpassword --db-name ecotaxa" &&
echo " db created" &&
docker exec -i portable_ecotaxaback_1 bash -c "PYTHONPATH=. python cmds/manage.py db build" &&
#replace adminstrator by a "valid" email
docker exec -i portable_pgdb_1 psql -U postgres -h localhost -d ecotaxa -c "UPDATE users SET email='administrator@mail.test' WHERE id=1;"  &&
echo "connect with administrator@mail.test" &&
docker stop portable_ecotaxaback_1 &&
echo " end install" &&
docker-compose -p portable up &&
echo "http://localhost:8088"