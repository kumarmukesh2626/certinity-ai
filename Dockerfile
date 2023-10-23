FROM python:3.8-slim-buster

COPY . /app

WORKDIR /app

RUN pip install --upgrade cython

RUN apt-get -y update

RUN pip install --upgrade pip

RUN apt-get install -y libgl1-mesa-glx

RUN apt-get install -y libglib2.0-0

RUN apt-get install -y nano

RUN pip install flask

RUN pip install flask_sqlalchemy

RUN pip install pymysql  # For MySQL database

RUN pip install psycopg2-binary  # For PostgreSQL database

EXPOSE 5002

CMD ["python", "alert_app.py"]

