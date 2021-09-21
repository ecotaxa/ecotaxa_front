# INSTALL ECOTAXA SYSTEM LOCALLY ON A PC (Ubuntu)
### Please fix this doc when you use it and find improvements
##
# I) To perform regularly : (reboot, softwares updates, components stopped or crashed)
## 1) Get the last versions, inside ...ecotaxa_dev folder, run
```
git pull
```
## 2) Check how postgresql is running
### To see if the command is understood, even if an error (e.g. about the role) is returned
```
psql
```
### To get info about the postgresql process
```
sudo systemctl status postgresql
```
### postgresql should be present as a running service, in the following results list
```
service --status-all
```
### To see the postgresql daemon
```
ps ax | grep postgresql
```
## 3) Start or restart postgresql
### You may need to restart postgresql if the backend docker has been stopped or after a PC reboot
### (postgresql does not like when the backend docker stops (but it's ok if the backend docker is not running)).
### (If the backend docker stops, then postgresql needs to be restarted)
```
service postgresql restart
```
### see point 2) to verify that it is running
###
## 4) Run the backend docker
### You may need to stop properly the backend docker before running run_docker.sh
```
docker stop ecotaxaback
docker rm ecotaxaback
```
### Then launch the backend docker
### (You may need to get the lastest backend version : see step 8)
```
./run_docker.sh
```
### hereunder an example of run_docker.sh, to adapt according to your ecotaxa_dev directory
```
#!/bin/bash
# 33:33 is www-data
# Add -i for having a console:
#docker run -it --rm \
docker run \
-u 1001:33 -p 8000:8000 --name ecotaxaback  \
-e "WEB_CONCURRENCY=4" -e "LEGACY_APP=/ecotaxa_master" \
--mount type=bind,source=/home/laurentr/ecotaxa/ecotaxa_dev,target=/ecotaxa_master  \
--mount type=bind,source=/var/run/postgresql,target=/var/run/postgresql  \
--mount type=bind,source=/home/laurentr/ecotaxa/ecotaxa_dev/plankton_rw,target=/plankton_rw \
grololo06/ecotaxaback:2.5
```
## 5) Activate the python environment by running, in the ~/ecotaxa/ecotaxa_dev directory
```
source venv/bin/activate
```
### When you see the "(venv)" prompt, you know that you got the python environment necessary for the spaghetti
### like : (venv) laurentr@laurentr-Latitude-7420:~$
## 6) Launch the spaghetti **from the venv environment**, in the ~/ecotaxa/ecotaxa_dev directory
```
python3 runserver.py
```
###
## 7) Run frontend locally: 0.0.0.0:5001 (or something like 0.0.0.0:8080 if you have another local frontend)

###
## 8) To update the backend version :
```
docker images
docker rmi  <<current ecotaxaback docker image reference>> --force
docker pull grololo06/ecotaxaback:<<last backend version>>
```
### Then update run_docker.sh with the appropriate backend version (see step 4)


## FROM HERE, NOT FINISHED
## FROM HERE, NOT FINISHED
## FROM HERE, NOT FINISHED
## FROM HERE, NOT FINISHED


# II) Prerequisites
## postgresql, python3, docker, git, apt, pip3 (TODO : more details)
### To see if postgresql is installed
```
apt list --installed | grep postgresql
```
### Some configuration work
Postgresql Startup + its configuration changes : n.b. this is done for version 13 of Postgresql
"sudo bash"
"cd /etc/postgresql/13/main" : this is the directory for configuring, while /var/lib/postgresql is for data
Make a change inside pg_hba.conf (hba means host base authentification) : if not existing, add a line 'host all postgres 127.0.0.1/32 trust'
Make a change inside pg_hba.conf (hba means host base authentification) : if not existing, add a line 'host all postgres 172.17.0.1/24 trust'
Make a change inside postgresql.conf (global postgresql config) : listen_addresses to fill in : 'localhost,172.17.0.1' + maybe port to set to 5432 instead of 5434
"psql -h newecotaxa.obs-vlfr.fr -U zoo -d ecotaxa" to enter inside the Database management
ecotaxa=> "select * from <tab>" to see the available tables
"\q" to quit
### Create database if it does not exist
drop_create.sh 
#!/bin/bash
set -x
CONN="-U postgres -h localhost -p 5432"
cat << EOF | psql $CONN
drop DATABASE ecotaxa3;
EOF
cat << EOF | psql $CONN
create DATABASE ecotaxa3
WITH ENCODING='UTF8'
OWNER=postgres
TEMPLATE=template0 LC_CTYPE='C' LC_COLLATE='C' CONNECTION LIMIT=-1;
create USER zoo PASSWORD 'zoololo';
EOF
set +x
4) ===== Récup de la BD
==> ssh pour essayer d'envoyer le .zip d la DATABASE
ssh newecotaxa.obs-vlfr.fr -l reese 'cat /backups/postgres/20210630-ecotaxa.dump.gz' | gunzip | pv | psql -U postgres -h localhost -d ecotaxa3
==> puis, suite à pb de transfert, on simplifie
ssh newecotaxa.obs-vlfr.fr -l reese 'cat /backups/postgres/20210627-ecotaxa.dump.gz' > db.dump.gz
ou : zcat 20210630-ecotaxa.dump.gz | psql -U postgres -h localhost -d ecotaxa3
5) ===== Spaghetti Python : il ne supporte pas un restart de la BD
==> env pour python : for local execution
~/ecotaxa/ecotaxa_dev$ git pull
~/ecotaxa/ecotaxa_dev$ python3 -m venv venv  construire env, fait 1 seule fois
laurentr@laurentr-Latitude-7420:~/ecotaxa/ecotaxa_dev$ cd venv/
==> python, pour le spagetti python

(venv) laurentr@laurentr-Latitude-7420:~/ecotaxa/ecotaxa_dev$ pip3 install -r requirements.txt (fait une seule fois)
Puis faire pour lancer le spageti :
(venv) laurentr@laurentr-Latitude-7420:~/ecotaxa/ecotaxa_dev$ python3 runserver.py à chaque fois
==> si nécessaire, installation de composants manquants
pip3 list
pip3 install psycopg2
pip3 install psycopg2-binary
pip3 install urllib3
pip3 install certifi
pip3 install hyphenator
pip3 install matplotlib
pip3 install requests

cp run_docker.sh ~/SAUV
docker images ==> je dois voir ecotaxa
docker pull grololo06/ecotaxaback
or
you may have to pull a specific version like :
"docker pull grololo06/ecotaxaback:2.5"
"docker rmi 4b39ceee4905 --force" if necessary (when you cannot remove an image because already running in a container)
"docker images purge" and/or "docker images prune"
~/ecotaxa/ecotaxa_dev/vault
~/ecotaxa/ecotaxa_dev/plankton_rw
cd ~/ecotaxa/ecotaxa_dev
~/ecotaxa/ecotaxa_dev$> . ./run_docker.sh  g changé le premier 33 en 1001
docker ps pour savoir les containers dockers qui tournent






6) ===== docker du backend
docker stop ecotaxaback  si nécessaire avant le run_docker.sh
docker rm ecotaxaback si nécessaire avant le run_docker.sh
cp run_docker.sh ~/SAUV
docker images ==> je dois voir ecotaxa
docker pull grololo06/ecotaxaback
or
you may have to pull a specific version like :
"docker pull grololo06/ecotaxaback:2.5"
"docker rmi 4b39ceee4905 --force" if necessary (when you cannot remove an image because already running in a container)
"docker images purge" and/or "docker images prune"
~/ecotaxa/ecotaxa_dev/vault
~/ecotaxa/ecotaxa_dev/plankton_rw
cd ~/ecotaxa/ecotaxa_dev
~/ecotaxa/ecotaxa_dev$> . ./run_docker.sh  g changé le premier 33 en 1001
docker ps pour savoir les containers dockers qui tournent

Fichiers personnalisés :
========================
drop_create.sh
run_docker.sh
~/ecotaxa/ecotaxa_dev/appli/__init__.py  ==> on avait commenté import matplotlib et matplotlib.use('Agg')
~/ecotaxa/ecotaxa_dev/requirements.txt ==> on avait commenté matplotlib==3.0.2
(cp config-model.cfg config.cfg)
config.cfg
pg_hba.conf  postgresql.conf (/etc/postgresql/13/main#)



Notes diverses :
================
NB : port 5001 pour le frontend python avec backend docker sur le port 8000

3 types d'erreur possibles, bien regarder les messages obtenus qui diffèrent.
Erreurs sur la base de données (ne tourne pas par exemple).
Errors on the python spageti (stopped).
Errors on the backend program ==>  Max retries exceeded with url: /users/me
http://localhost:5001 is the historic ecotaxa frontend running locally on my machine

!!! N.B : démarrer docker(le backend), (re)démarrer postgres sinon PB, puis spaghetti, puis le front (historic ou nouveau)
après un boot:
démarrer le back-end
voir que ça se gaufre
redémarrer postgres
démarrer le back-end
voir que c'est bon
spaghetti, front
** postgresql n'aime pas que le backend s'arrête (mais il supporte le backend non démarré), si ça se produit il a besoin de redémarrer
** le docker backend veut que postgresql soit dans un bon état quand il (re)démarre
** le spaghetti n'aime pas que postgresql redémarre, si ça se produit il a besoin de redémarrer

sinon g retrouvé des modifs qu'on avait faites :
~/ecotaxa/ecotaxa_dev/appli/__init__.py  ==> on avait commenté avec un # import matplotlib et matplotlib.use('Agg')
~/ecotaxa/ecotaxa_dev/requirements.txt ==> on avait commenté avec un # matplotlib==3.0.2
Je sais pas si on tomberait sur le même problème
if you comment out, EcoPart will not work
