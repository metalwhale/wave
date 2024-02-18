FROM python:3.12.2-slim-bookworm

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt
