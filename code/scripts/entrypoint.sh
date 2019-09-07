#!/bin/sh

echo "waiting for DB "

while ! python manage.py migrate
do
  echo -n .
  sleep 4
done

exec "$@"
