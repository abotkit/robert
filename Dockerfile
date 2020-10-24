FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install -y curl

RUN pip install requests gunicorn

COPY requirements.txt /opt/botkit/requirements.txt
WORKDIR /opt/botkit

RUN pip install -r requirements.txt

COPY . /opt/botkit

EXPOSE 5000

ENV ABOTKIT_ROBERT_PORT=5000

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:$ABOTKIT_ROBERT_PORT", "robert:app"]