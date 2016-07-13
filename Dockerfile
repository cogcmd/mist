FROM alpine:3.4

MAINTAINER Kevin Smith <kevin@operable.io>

# Update package DB and install Python & git
USER root
RUN apk update -U && apk add --no-cache python3 git && python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && rm -rf /root/.cache

# Copy source
COPY . /mist

# Install deps and tidy up
RUN cd /mist && pip3 install -r meta/requirements.txt \
  && apk del git && rm -rf /var/cache/apk/* \
  && mkdir /usr/lib/python3.5/site-packages/mist \
  && cp -R /mist/lib/mist/* /usr/lib/python3.5/site-packages/mist \
  && chmod +x /mist/commands/* && mv /mist/commands/* /usr/local/bin \
  && rm -rf /mist && ln -s /usr/bin/python3 /usr/bin/python
