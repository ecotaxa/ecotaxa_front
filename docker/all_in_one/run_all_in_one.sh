#!/bin/sh
docker compose  -f docker-compose.yml -p portable up &&
echo "http://localhost:8088"