FROM python:3.8-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update -y

RUN pip install --upgrade pip
RUN pip install pipenv

COPY . /app/

RUN pipenv lock
RUN pipenv install --dev --deploy --system
RUN python -m pytest
