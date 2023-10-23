FROM python:3.8-slim-buster

COPY . /app

WORKDIR /app

RUN pip install --upgrade cython

RUN apt-get -y update

RUN pip install --upgrade pip

RUN apt install -y libgl1-mesa-glx

RUN apt install -y libglib2.0-0

RUN apt install nano

RUN pip install flask_sqlalchemy

RUN pip install PyMysql

RUN pip install psycopg2-binary

EXPOSE 5002

CMD ["python","alert_app.py"]
