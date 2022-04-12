FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -yq librdkafka-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_lg

COPY . .

ENV PYTHONUNBUFFERED True

CMD exec gunicorn --bind :80 --workers 1 --threads 8 --timeout 0 --log-level=debug main:app
