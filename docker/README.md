Present docker builder exposes a uwsgi port.

Example run command:

    docker run --rm --name ecotaxafront \ 
    -u 1000:1000 --network host \
    -v $PWD/../appli/config.cfg:/app/appli/config.cfg \ 
    ecotaxa/ecotaxafront 

The --network host is necessary for now for the front-end to be able to reach the back-end on same machine.

### Pseudo-prod testing

We'll need a network bridge, which is the cleanest way to have docker instances communicate,
@see https://docs.docker.com/network/bridge/

    docker network create econet

#### EcoTaxa back:

    docker run --name ecotaxaback \
    --network econet -u 1000:1000 \
    -e "WEB_CONCURRENCY=2" \
    --mount type=bind,source=$PWD/../py/config.ini,target=/config.ini  \
    --mount type=bind,source=/vieux,target=/vieux  \
    --mount type=bind,source=/home/laurent/Devs/ecotaxa/SrvFics/,target=/home/laurent/Devs/ecotaxa/SrvFics \
    ecotaxa/ecotaxa_back

**Note**: Due to: https://github.com/portainer/portainer/issues/4518 it's better to use -v if you intend to use portainer to
recreate containers.

    docker run --name ecotaxaback \
    --network econet -u 1000:1000 \
    -e "WEB_CONCURRENCY=2" \
    -v $PWD/../py/config.ini:/config.ini  \
    -v /vieux:/vieux  \
    -v /home/laurent/Devs/ecotaxa/SrvFics/:/home/laurent/Devs/ecotaxa/SrvFics \
    ecotaxa/ecotaxa_back:2.6.2

#### EcoTaxa front:

    docker run --rm --name ecotaxafront \
    --network econet -u 1000:1000 \
    -v $PWD/../appli/config.cfg:/app/appli/config.cfg \
    ecotaxa/ecotaxa_front

#### Nginx reverse proxy:

    docker run --rm --name nginx \ 
    --network econet -p 8082:80 \
    -v $PWD/nginx.conf:/etc/nginx/nginx.conf \
    -v $PWD/../../ecotaxa_back/vault:/eco_data/vault \
    nginx

You can now connect to `localhost:8082`.

