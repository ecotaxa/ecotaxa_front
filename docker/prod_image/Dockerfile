FROM ubuntu:20.04 as builder

MAINTAINER grololo06 <grololo06@users.noreply.github.com>

RUN apt-get update

RUN apt-get install \
    vim \
    uwsgi uwsgi-plugin-python3 \
    python3.8 python3.8-venv \
    --no-install-recommends --yes

# Create venv
RUN python3.8 -m venv /venv
# Install wheel & upgrade pip
RUN PATH=/venv/bin pip3 install --upgrade pip wheel
RUN PATH=/venv/bin:$PATH pip3 install -r requirements.txt

# Strip a bit...
RUN find /venv -name "*.pyc" -delete && \
rm -rf /venv/share/* && \
find /venv -name tests -type d -exec rm -rf {} + && \
find /venv/lib/python3.8/site-packages -name "*.exe" -delete

# Get source
WORKDIR /app/
COPY . ./
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
