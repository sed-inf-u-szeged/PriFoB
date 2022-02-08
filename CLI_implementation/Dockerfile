FROM python:3.8-slim-buster

WORKDIR /app

RUN apt update
RUN apt install -y python3-rsa

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p local_files/credentials
RUN mkdir -p local_files/keys
RUN mkdir -p local_files/schemes

COPY . .

EXPOSE 5050

CMD ["python", "prifob.py"]