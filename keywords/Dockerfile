FROM python:3

ARG REGISTRY_PROJECT

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -yq librdkafka-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-pypi.txt ./
RUN pip install --no-cache-dir -r requirements-pypi.txt
COPY requirements-isidro.txt ./
RUN pip install --no-cache-dir -r requirements-isidro.txt --extra-index-url https://us-python.pkg.dev/$REGISTRY_PROJECT/isidro-libs/simple/

RUN python -m spacy download en_core_web_lg

COPY . .

ENV PYTHONUNBUFFERED True

CMD exec gunicorn --bind :80 --workers 1 --threads 8 --timeout 0 --log-level=debug main:app
