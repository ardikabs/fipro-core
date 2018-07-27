#!/bin/bash

celery worker -A celery_worker.celery --loglevel=info &
celery beat -A celery_worker.celery --loglevel=info &
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:8000 --reload wsgi

