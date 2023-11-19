FROM python:3.11.3
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN pip install psycopg2
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app


