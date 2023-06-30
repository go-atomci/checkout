FROM python:3.6.15-alpine

COPY scripts/  /usr/local/bin/

RUN apk add --update --no-cache git git-lfs && pip install -r /usr/local/bin/requirements.txt  \
        && chmod +x /usr/local/bin/*.py