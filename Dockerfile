FROM python:3.11.1-alpine as base

# Image config
ENV APP_USER=stock-ticker
ENV APP_DIR=/app

WORKDIR ${APP_DIR}

RUN apk update && apk add curl

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN adduser -D -h ${APP_DIR} ${APP_USER}

# Change user so the image does not run as root
USER ${APP_USER}

#########################################
### Copy the app code and run unicorn ###
#########################################
FROM base as api

COPY app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]


#########################################
### Extra stage for running the tests ###
#########################################
FROM base as test

USER root

COPY test/requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY app/ .

COPY test/ .

CMD ["pytest", "-vv", "--cov"]
