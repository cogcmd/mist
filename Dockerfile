FROM gliderlabs/alpine:3.3

MAINTAINER Kevin Smith <kevin@operable.io>

# Update package DB and install Python & git
RUN apk-install \
    python \
    py-pip \
    python-dev \
    git

# Copy source
COPY . /mist

# Install deps and tidy up
RUN cd /mist && pip install -r meta/requirements.txt \
  && apk del git && rm -rf /var/cache/apk/*

RUN mkdir /usr/lib/python2.7/site-packages/mist \
  && cp -R /mist/lib/mist/* /usr/lib/python2.7/site-packages/mist

RUN chmod +x /mist/commands/* && mv /mist/commands/* /usr/local/bin
RUN rm -rf /mist
