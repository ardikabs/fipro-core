#!/usr/bin/env python
import os

from app import create_app
from app.extensions.celery import make_celery


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()

celery = make_celery(app)

from app.extensions.celery import tasks
