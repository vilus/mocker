FROM python:3.7

ENV PYTHONUNBUFFERED 1

ARG DJANGO_STATIC_ROOT
ENV DJANGO_STATIC_ROOT ${DJANGO_STATIC_ROOT:-/static_files_default}

RUN mkdir /code
WORKDIR /code
COPY requirements.txt ./

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./code .

RUN python manage.py collectstatic --noinput

ENTRYPOINT ["./scripts/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "--nostatic", "0.0.0.0:8080"]
