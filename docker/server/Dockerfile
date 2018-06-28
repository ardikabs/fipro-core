FROM python:3.6-alpine


ADD project/ /project

WORKDIR /project
RUN pip install -r requirements.txt \
    && python manage.py recreate_db \
    && python setup_dev

EXPOSE 8080/tcp
CMD ["gunicorn","-w","4","-b","0.0.0.0:8080","wsgi"]