FROM python:3

RUN apt-get update -qqy && \
    apt-get install -qqy --no-install-recommends \
        tini && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED True

CMD exec gunicorn --bind :80 --workers 1 --threads 8 --timeout 0 --log-level=debug main:app
