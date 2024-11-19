FROM python:3.11-slim

RUN apt-get update \
  && apt-get -y install tesseract-ocr \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY main.py .
COPY image2text.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
