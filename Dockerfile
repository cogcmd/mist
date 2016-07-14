FROM alpine:3.4

MAINTAINER Kevin Smith <kevin@operable.io>

# Update package DB and install Python & git
USER root
RUN apk update -U && apk add --no-cache python3 git && python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && rm -rf /root/.cache

RUN adduser -h /home/bundle -D bundle

COPY setup.py requirements.txt /home/bundle/mist/
COPY mist/*.py /home/bundle/mist/mist/
COPY mist/commands/*.py /home/bundle/mist/mist/commands/

WORKDIR /home/bundle/mist
RUN pip3 install -r requirements.txt .
