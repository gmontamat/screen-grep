# screen-grep

A privacy-oriented, open-source alternative
to [Windows Recall](https://support.microsoft.com/en-us/windows/retrace-your-steps-with-recall-aa03f8a0-a78b-4b3e-b0a1-2eb8ac48701c),
crafted for simplicity, and oriented on local data storage and model inference. This solution consists of the following
components:

* [screenshot](src/screenshot): capture screenshots of your active window on a regular interval
* [caption](src/caption): run image-to-text and OCR models locally to create text captions from the screenshots
* elasticsearch: text search engine
* [search](src/search): webapp to find content from previous screenshots

## How to run

```shell
docker compose up -d
```

**Note**: the screenshot service in docker is still a WIP and may not work properly.

## Development setup

Start the `screenshot` capturing script:

```shell
./src/screenshot/screenshot.sh
```

Next, start an [elasticsearch](https://www.elastic.co/elasticsearch) container with docker to store processed captions:

```shell
docker run --rm -it -e discovery.type=single-node -p 9200:9200 docker.elastic.co/elasticsearch/elasticsearch:7.10.1
```

To process the images into the searchable database, run:

```shell
pip install -r src/caption/requirements.txt
python src/caption/main.py
```

Finally, start the [webapp](http://127.0.0.1:5000) to search previous screenshots:

```shell
pip install -r src/search/requirements.txt
python src/search/app.py
```

# TODO

- [ ] Complete docker compose setup
- [ ] Improve search algorithm (use embeddings and fuzzy search?)
