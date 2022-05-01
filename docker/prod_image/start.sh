#! /usr/bin/env sh
set -e
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
if [ ! -e /app/config/config.cfg ]; then
  echo "CANNOT START: No /app/config/config.cfg !"
  exit
fi
exec uwsgi --ini /app/uwsgi.ini
