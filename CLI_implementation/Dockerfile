FROM python:3.8-slim-buster

WORKDIR /app

RUN apt update
RUN apt install -y python3-rsa

RUN pip install cryptography
RUN pip install rsa
RUN pip install tabulate

RUN mkdir -p local_files/credentials
RUN mkdir -p local_files/keys
RUN mkdir -p local_files/schemes

COPY . .

EXPOSE 5050

CMD ["python", "prifob.py"]