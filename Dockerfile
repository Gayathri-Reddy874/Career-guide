FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD exec gunicorn --bind :8080 app:app