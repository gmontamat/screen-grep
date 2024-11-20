import os
import shutil

from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)

# Get directory for images
IMAGES_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "images")
os.makedirs(IMAGES_PATH, exist_ok=True)
# Initialize Elasticsearch client
ES_HOST = os.getenv("ES_HOST", "localhost")
es = Elasticsearch([f"http://{ES_HOST}:9200"])


def move_images(image_path):
    """
    Move an image to the IMAGES_PATH directory if it does not
    already exist there.
    """
    filename = os.path.basename(image_path)
    if not os.path.isfile(os.path.join(IMAGES_PATH, filename)):
        shutil.move(image_path, IMAGES_PATH)


@app.route("/", methods=["GET", "POST"])
def search():
    ocr_results = []
    caption_results = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            # Search in Elasticsearch for OCR matches
            ocr_response = es.search(
                index="screenshots",
                body={
                    "query": {
                        "match": {
                            "ocr": query
                        }
                    }
                }
            )
            ocr_results = ocr_response["hits"]["hits"]
            for result in ocr_results:
                move_images(result["_source"]["image_path"])
                result["_source"]["image_path"] = os.path.basename(result["_source"]["image_path"])

            # Search in Elasticsearch for Caption matches
            caption_response = es.search(
                index="screenshots",
                body={
                    "query": {
                        "match": {
                            "caption": query
                        }
                    }
                }
            )
            caption_results = caption_response["hits"]["hits"]
            for result in caption_results:
                move_images(result["_source"]["image_path"])
                result["_source"]["image_path"] = os.path.basename(result["_source"]["image_path"])
    return render_template("search_results.html", ocr_results=ocr_results, caption_results=caption_results)


@app.route("/display/<screenshot_id>")
def display(screenshot_id):
    # Retrieve the document by ID
    response = es.get(index="screenshots", id=screenshot_id)
    result = response["_source"]
    result["image_path"] = os.path.basename(result["image_path"])
    return render_template("display.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
