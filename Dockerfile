FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install -y curl

COPY requirements.txt /opt/robert/requirements.txt
WORKDIR /opt/robert

RUN pip install -r requirements.txt

COPY . /opt/robert

EXPOSE 5000
ENV ABOTKIT_ROBERT_PORT=5000

CMD ["uvicorn", "robert:app", "--port", ABOTKIT_ROBERT_PORT]