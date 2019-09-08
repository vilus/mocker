#!/bin/sh

echo "waiting for DB "


attempt=1
while ! python manage.py migrate --noinput
do
  if [ $attempt -le 15 ]
  then
    break
  fi
  attempt=$(( $attempt + 1 ))

  echo -n .
  sleep 1
done

exec "$@"
