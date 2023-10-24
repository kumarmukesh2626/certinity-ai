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

RUN pip install requests  # For sending HTTP requests

RUN pip install pillow  # For working with images (PIL)

# If you need Apache Tika for text extraction from documents

 # If you need to extract text from PDFs

RUN pip install openpyxl  # For working with Excel files

RUN pip install pandas  # For data manipulation with Pandas

EXPOSE 5002

CMD ["python", "alert_app.py"]

