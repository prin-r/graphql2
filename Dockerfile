FROM python:3.6.8-alpine3.8

WORKDIR /app

COPY . /app

RUN \
  apk add --no-cache postgresql-libs && \
  apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
  pip install --trusted-host pypi.python.org -r requirements.txt

ENV JSON_RPC_URL http://172.18.0.7:8545

CMD ["python", "__main__.py", "--dburi=postgresql://postgres:1234@172.18.0.6:5432", "--dbname=graph_test", "LOOP"]
