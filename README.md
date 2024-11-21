# screen-grep

A privacy-oriented, OS-agnostic, open-source alternative
to [Windows Recall](https://support.microsoft.com/en-us/windows/retrace-your-steps-with-recall-aa03f8a0-a78b-4b3e-b0a1-2eb8ac48701c),
crafted for simplicity, and oriented on local data storage and model inference. This solution consists of the following
components:

* [screenshot](src/screenshot): script that captures screenshots of your active window on a regular interval
* [caption](src/caption): run image-to-text and OCR models locally to create text captions from the screenshots
* elasticsearch: text search engine
* [search](src/search): webapp to find content from previous screenshots

## How to run

Start the screenshot capturing script (which isn't dockerized yet):

```shell
./src/screenshot/screenshot.sh 10  # Screenshot every 10 seconds
```

It should begin collecting screenshots from your active window under `data/screenshots`.

**TIP**: you can stop this script to stop capturing new screenshots while still running the search service.

Next, run the search app:

```shell
docker compose up -d
```

You can search for previous screenshots in http://localhost:5000/

## Local development setup

Start the screenshot capturing script:

```shell
./src/screenshot/screenshot.sh
```

Run an [elasticsearch](https://www.elastic.co/elasticsearch) container in docker to store processed captions:

```shell
docker run --rm -it -e discovery.type=single-node -p 9200:9200 docker.elastic.co/elasticsearch/elasticsearch:7.10.1
```

To add the screenshots to the searchable database, run:

```shell
pip install -r src/caption/requirements.txt
export HF_HOME=data/models  # Optionally store huggingface cache in current dir
python src/caption/main.py
```

Start the [webapp](http://127.0.0.1:5000) to search previous screenshots:

```shell
pip install -r src/search/requirements.txt
python src/search/app.py
```

# TODO

- [ ] Move the screenshot script in docker
- [ ] Regex to isolate hyperlinks from screenshots
- [ ] Support macos, windows
- [ ] Improve search algorithm (use embeddings and fuzzy search)
- [ ] Add LLM chat support (eg: be able to ask "how much time have I been working on my IDE today?")
