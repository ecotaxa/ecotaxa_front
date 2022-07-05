
PRE-REQUISITES:

Install Docker on your computer. On Mac OS and Windows, install Docker Desktop from https://www.docker.com/products/docker-desktop/.
Tested Linux, Windows and Mac OS (but amd64 and M1 architectures).

HOWTO:

In same directory as present file, and a system-native shell (e.g. CMD.exe on windows):

$ docker-compose -p portable up

All services will bring up, and spit tons of errors as there is no database yet.

In another shell, so the docker-compose still runs and provides output, list the created docker images:

$ docker ps

The back-end docker should appear in the list, and be running. Its name will likely be portable_ecotaxaback_1 or portable-ecotaxaback-1.

Now build the DB, using the found name:

$ docker exec -it portable-ecotaxaback-1 bash

and run the following commands:

root@97aab8baa6b0:/app# PYTHONPATH=. python cmds/manage.py db create --password mysecretpassword --db-name ecotaxa
root@97aab8baa6b0:/app# PYTHONPATH=. python cmds/manage.py db build
Adding user 'administrator'
root@97aab8baa6b0:/app# exit

The errors should stop in the first shell.
You should now be able to connect to http://localhost:8088 using administrator/ecotaxa

Before e.g. trying to import some data, it's better to fetch the official taxonomy tree, by using http://localhost:8088/taxo/browse/ (and waiting...)
