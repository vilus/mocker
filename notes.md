docker-compose build
docker-compose up -d
docker-compose down -v

firewall-cmd --zone=public --add-port=8080/tcp --permanent

docker-compose run mocker python manage.py migrate
