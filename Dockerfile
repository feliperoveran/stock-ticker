FROM python:3.11.1-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app/ .

# TODO: move to separate image step
COPY test/ .

# TODO: do not run as root
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
