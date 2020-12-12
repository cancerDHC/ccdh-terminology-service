FROM python:3.8

RUN pip install pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY . /app
COPY docker/.env /app/.env

WORKDIR /app
CMD uvicorn ccdh.api.app:app $ROOT_PATH --host 0.0.0.0 --port 80