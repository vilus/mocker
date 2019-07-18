docker-compose build
docker-compose up -d
docker-compose down -v

firewall-cmd --zone=public --add-port=8080/tcp --permanent

docker-compose run --rm srv python manage.py migrate

docker-compose run --rm --no-deps srv pytest
