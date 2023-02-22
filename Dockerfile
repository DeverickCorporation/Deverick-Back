FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN apt-get update \
    && apt-get -y install libpq-dev gcc 
RUN pip install -r requirements.txt
EXPOSE 8003
CMD gunicorn -w 1 -b 0.0.0.0:8003 --timeout 3600 "run_server:app"
COPY . /app
