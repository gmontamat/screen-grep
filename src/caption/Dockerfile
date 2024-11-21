FROM python:3.11-slim

RUN apt-get update \
  && apt-get -y install curl tesseract-ocr \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
