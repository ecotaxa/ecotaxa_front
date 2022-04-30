#! /usr/bin/env sh
set -e
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
if [ ! -e /app/appli/config.cfg ]; then
  echo "CANNOT START: No /app/appli/config.cfg !"
  exit
fi
exec uwsgi --ini /app/uwsgi.ini
