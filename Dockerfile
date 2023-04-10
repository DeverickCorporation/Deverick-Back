FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get -y install libpq-dev gcc 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn -w 1 -b 0.0.0.0:5000 --timeout 3600 "run_server:app"
