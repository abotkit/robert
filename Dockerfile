FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install -y curl

COPY requirements.txt /opt/robert/requirements.txt
WORKDIR /opt/robert
RUN mkdir logs

RUN pip install -r requirements.txt

COPY . /opt/robert

EXPOSE 5000
ENV ABOTKIT_ROBERT_PORT=5000

ENTRYPOINT gunicorn robert:app -b 0.0.0.0:${ABOTKIT_ROBERT_PORT} -p robert.pid -k uvicorn.workers.UvicornWorker --timeout 120 --workers=1 --access-logfile /opt/robert/logs/access.log --log-level DEBUG --log-file /opt/robert/logs/app.log