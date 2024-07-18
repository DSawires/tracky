# Use the official Python image from the Docker Hub
FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV FLASK_APP=app

EXPOSE 5000

CMD ["python", "app.py"]
