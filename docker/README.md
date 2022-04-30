Present docker builder exposes a uwsgi port.

Example run command:

    docker run --rm --name ecotaxafront \ 
    -u 1000:1000 --network host \
    -v $PWD/../appli/config.cfg:/app/appli/config.cfg \ 
    ecotaxa/ecotaxafront 

The --network host is necessary for now for the front-end to be able to reach the back-end on same machine.