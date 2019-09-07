FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt ./

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./code .

ENTRYPOINT ["./scripts/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
