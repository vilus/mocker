#!/bin/sh

echo "waiting for DB "

while ! python manage.py migrate --noinput
do
  echo -n .
  sleep 1
done

exec "$@"
