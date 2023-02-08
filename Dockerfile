FROM python:3.11.1-alpine as api

# Image config
ENV APP_USER=stock-ticker
ENV APP_DIR=/app

WORKDIR ${APP_DIR}

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN adduser -D -h ${APP_DIR} ${APP_USER}

# Change user so the image does not run as root
USER ${APP_USER}

COPY ${APP_DIR} .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]


#########################################
### Extra stage for running the tests ###
#########################################
FROM api as test

USER root

COPY test/requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY test/ .

CMD ["pytest", "-vv", "--cov"]
