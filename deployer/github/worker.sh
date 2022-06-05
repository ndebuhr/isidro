#!/usr/bin/env sh

celery -A main.tasks worker --loglevel=info