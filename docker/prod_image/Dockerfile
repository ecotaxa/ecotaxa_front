FROM ubuntu:22.04 AS builder

LABEL maintainer="grololo06 <grololo06@users.noreply.github.com>"

RUN apt-get update && \
    apt-get install -y software-properties-common

RUN add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y \
    curl ca-certificates \
    vim build-essential gcc \
    python3.13 python3.13-dev python3.13-venv

# Install pip specifically for Python 3.13
RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.13 get-pip.py

#  Use freshly installed pip to build uwsgi
RUN python3.13 -m pip install uwsgi

# Get source
WORKDIR /app/
COPY py ./

# Create venv
RUN python3.13 -m venv /venv
# Install wheel & upgrade pip
RUN PATH=/venv/bin pip3 install wheel
RUN PATH=/venv/bin:$PATH pip3 install -r requirements.txt

# Strip a bit...
RUN find /venv -name "*.pyc" -delete && \
    rm -rf /venv/share/* && \
    find /venv -name tests -type d -exec rm -rf {} + && \
    find /venv/lib/python3.13/site-packages -name "*.exe" -delete && \
    rm -rf /var/lib/apt/lists/*

# Get starting script and fixed config
COPY docker/prod_image/start.sh /app
COPY docker/prod_image/uwsgi.ini /app

## For /app/*.log and **/__pycache__, allow non-root user to create inside dirs
## and fix startup script rights
RUN find /venv /app -type d -exec chmod a+w {} \; && \
chmod +x /app/start.sh

# uwsgi port
EXPOSE 3030

WORKDIR /app/

CMD ["./start.sh"]