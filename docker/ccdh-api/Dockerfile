FROM python:3.8

#RUN pip install pipenv
#COPY Pipfile* /tmp/
#RUN cd /tmp && pipenv lock --requirements > requirements.txt
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY . /app
#COPY docker/.env /app/.env
COPY .env /app/.env
COPY .env.prod /app/.env.prod
COPY .env.test /app/.env.test

WORKDIR /app
#CMD pipenv run uvicorn ccdh.api.app:app $ROOT_PATH --host 0.0.0.0 --port 8000
CMD uvicorn ccdh.api.app:app $ROOT_PATH --host 0.0.0.0 --port 8000
