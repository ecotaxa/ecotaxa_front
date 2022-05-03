
PRE-REQUISITES:

Docker tool on your PC. Tested only on amd64 processor family.

HOWTO:

In same directory as present file:

$ docker-compose -p portable up

All services will bring up, and spit tons of errors as there is no database yet.

Now build the DB:

$ docker exec -it portable_ecotaxaback_1 bash
root@97aab8baa6b0:/app# PYTHONPATH=. python cmds/manage.py db create --password mysecretpassword --db-name ecotaxa
root@97aab8baa6b0:/app# PYTHONPATH=. python cmds/manage.py db build
Adding user 'administrator'
root@97aab8baa6b0:/app# exit

You should be able to connect to http://localhost:8088 using administrator/ecotaxa


