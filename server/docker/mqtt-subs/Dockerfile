

FROM python:3.6-alpine


ADD collector/ /collector

WORKDIR /collector
RUN pip install -r requirements.txt


CMD ["python", "main.py"]
