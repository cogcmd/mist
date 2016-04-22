FROM gliderlabs/alpine:latest

MAINTAINER Kevin Smith <kevin@operable.io>

# Update package DB and install Python & git
RUN apk-install \
    python \
    py-pip \
    python-dev \
    ca-certificates

# Copy source
COPY . /mist

# Install deps and tidy up
RUN apk-install git && cd /mist && pip install -r meta/requirements.txt \
  && apk del git && rm -rf /var/cache/apk/* \
  && mkdir /usr/lib/python2.7/site-packages/mist \
  && cp -R /mist/lib/mist/* /usr/lib/python2.7/site-packages/mist \
  && chmod +x /mist/commands/* && mv /mist/commands/* /usr/local/bin \
  && rm -rf /mist
