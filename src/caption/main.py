import os
import shutil
import subprocess
import time

from elasticsearch import Elasticsearch
from image2text import FlorenceCaption, TesseractOCR

IMAGE2TEXT_MODEL = FlorenceCaption()
OCR_MODEL = TesseractOCR()
ES_HOST = os.getenv("ES_HOST", "localhost")
SCREENSHOTS = "data/screenshots"
PROCESSED = "data/processed"


def caption_images(input_path: str, output_path: str, es: Elasticsearch):
    for filename in os.listdir(input_path):
        file_path = os.path.join(input_path, filename)
        if os.path.isfile(file_path) and file_path.lower().endswith((".png", ".jpg", ".jpeg")):
            # image2text model
            caption = IMAGE2TEXT_MODEL.generate_caption(file_path)
            # OCR
            ocr = "No OCR"  # OCR_MODEL.generate_caption(file_path)
            # Move image to done
            shutil.move(file_path, output_path)
            # Add entry to elasticsearch
            image_path = os.path.abspath(os.path.join(output_path, filename))
            es.index(index="screenshots", document={"ocr": ocr, "caption": caption, "image_path": image_path})


if __name__ == "__main__":
    subprocess.run([f"{os.path.dirname(__file__)}/init-index.sh"])
    db = Elasticsearch([f"http://{ES_HOST}:9200"])
    if not os.path.exists(PROCESSED):
        os.makedirs(PROCESSED, exist_ok=True)
    while True:
        caption_images(SCREENSHOTS, PROCESSED, db)
        time.sleep(300)  # Sleep for 5 minutes (300 seconds) before the next call
