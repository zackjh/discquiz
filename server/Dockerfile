# syntax=docker/dockerfile:1

FROM python:3.12.1-slim-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["flask", "--app", "api.py", "run", "--host=0.0.0.0"]