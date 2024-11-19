import os

from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)

# Initialize Elasticsearch client
ES_HOST = os.getenv("ES_HOST", "localhost")
es = Elasticsearch([f"http://{ES_HOST}:9200"])


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
    return render_template("search_results.html", ocr_results=ocr_results, caption_results=caption_results)


@app.route("/image/<id>")
def show_image(_id):
    # Retrieve the document by ID
    response = es.get(index="screenshots", id=_id)
    result = response["_source"]
    return render_template("full_image.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
