# Builder stage
FROM ubuntu:22.04 AS builder

LABEL maintainer="grololo06 <grololo06@users.noreply.github.com>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    curl ca-certificates \
    build-essential gcc \
    python3.13 python3.13-dev python3.13-venv

# Install pip specifically for Python 3.13
RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.13 get-pip.py

# Create venv and install dependencies
RUN python3.13 -m venv /venv
RUN /venv/bin/pip install --no-cache-dir --upgrade pip wheel
RUN /venv/bin/pip install --no-cache-dir uwsgi

WORKDIR /build
COPY py/requirements.txt ./
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Strip unnecessary files from venv
RUN find /venv -name "*.pyc" -delete && \
    rm -rf /venv/share/* && \
    find /venv -name tests -type d -exec rm -rf {} + && \
    find /venv/lib/python3.13/site-packages -name "*.exe" -delete

# Runner stage
FROM ubuntu:22.04

LABEL maintainer="grololo06 <grololo06@users.noreply.github.com>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.13 \
    libpython3.13 \
    libxml2 \
    libpq5 \
    && apt-get purge -y --auto-remove software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy venv and app
COPY --from=builder /venv /venv
WORKDIR /app/
COPY py ./
COPY prod_image/start.sh /app/
COPY prod_image/uwsgi.ini /app/

# For /app/*.log and **/__pycache__, allow non-root user to create inside dirs
# and fix startup script rights
RUN find /venv /app -type d -exec chmod a+w {} \; && \
    chmod +x /app/start.sh

# uwsgi port
EXPOSE 3030

# Ensure uwsgi from venv is used
ENV PATH="/venv/bin:$PATH"

CMD ["./start.sh"]