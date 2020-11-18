FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install -y curl wget unzip

COPY requirements.txt /opt/robert/requirements.txt
WORKDIR /opt/robert

RUN pip install -r requirements.txt

COPY . /opt/robert

EXPOSE 5000
ENV ABOTKIT_ROBERT_PORT=5000

ENTRYPOINT gunicorn robert:app -b 0.0.0.0:${ABOTKIT_ROBERT_PORT} -k uvicorn.workers.UvicornWorker --timeout 600 --workers=1 --log-level DEBUG
