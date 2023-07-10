FROM python:3.11.4-alpine
WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /usr/src/requirements.txt

RUN pip install -r /usr/src/requirements.txt

COPY . /usr/src

COPY ./pre_start.sh /usr/src
COPY ./migrate.sh /usr/src

ENV PYTHONPATH /usr/src/

RUN chmod +x /usr/src/pre_start.sh
RUN chmod +x /usr/src/migrate.sh