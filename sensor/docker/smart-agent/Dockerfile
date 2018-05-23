

FROM python:3.6-alpine


ADD project/ /project

WORKDIR /project
RUN pip install -r requirements.txt

EXPOSE 5000/tcp
ENTRYPOINT ["/bin/bash"]
CMD ["python", "manage.py","runserver"]
