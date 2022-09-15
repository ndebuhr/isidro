FROM python:3-alpine

ENV PORT 8080

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED True

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --log-level=debug main:app
