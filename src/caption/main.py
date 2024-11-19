import os
import shutil
import subprocess
import time

from elasticsearch import Elasticsearch
from image2text import FlorenceCaption, TesseractOCR

IMAGE2TEXT_MODEL = FlorenceCaption()
OCR_MODEL = TesseractOCR()
SCREENSHOT_DIR = "data/screenshots"
PROCESSED_DIR = "data/processed"
ES_HOST = os.getenv("ES_HOST", "localhost")


def caption_images(input_path: str, output_path: str, es: Elasticsearch):
    for filename in os.listdir(input_path):
        file_path = os.path.abspath(os.path.join(input_path, filename))
        if os.path.isfile(file_path) and file_path.lower().endswith((".png", ".jpg", ".jpeg")):
            # image2text model
            caption = IMAGE2TEXT_MODEL.generate_caption(file_path)
            # OCR
            ocr = OCR_MODEL.generate_caption(file_path)
            # Move image to done
            shutil.move(file_path, output_path)
            # Add to elasticsearch
            es.index(index="screenshots", document={"ocr": ocr, "caption": caption, "image_path": filename})


if __name__ == "__main__":
    subprocess.run(["./init-index.sh"])
    db = Elasticsearch([f"http://{ES_HOST}:9200"])
    while True:
        caption_images("data/screenshots", "data/processed", db)
        time.sleep(300)  # Sleep for 5 minutes (300 seconds) before the next call
