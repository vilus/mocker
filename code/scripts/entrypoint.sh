#!/bin/sh

echo "waiting for DB "


attempt=1
while ! python manage.py migrate --noinput
do
  if [ $attempt -gt 15 ]
  then
    exit 1
  fi
  attempt=$(( $attempt + 1 ))

  echo -n .
  sleep 1
done

exec "$@"
