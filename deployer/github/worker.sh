#!/usr/bin/env bash

celery -A main.tasks worker --loglevel=info