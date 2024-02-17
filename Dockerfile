FROM python:3.12
LABEL authors="maxim"

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install gunicorn django-celery-beat django-cors-headers

COPY ./requirements.txt .

RUN pip install -r requirements.txt
COPY . .