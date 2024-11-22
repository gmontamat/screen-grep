# screen-grep

<p align="center">
  <img src="assets/app.gif" />
</p>

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

If you're running a Windows OS, see how to use the alternative [screenshot PowerShell script](#screenshots-in-windows).

This scrip should begin collecting screenshots from your active window under `data/screenshots`.

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

## Screenshots in Windows

To capture screenshots in Windows, use [this PowerShell script](src/screenshot/screenshot.ps1). In order to run it, you
should change the default PowerShell's execution policy, which restricts the running of scripts for security reasons:

1. Search for "PowerShell" in the Start menu.
2. Right-click on "Windows PowerShell" and select "Run as administrator."
3. Run the following command to set the execution policy to allow running scripts:
    ```shell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
    ```

Once the policy is set, right-click on the [PowerShell script](src/screenshot/screenshot.ps1) and select
"Run with PowerShell."

# TODO

- [ ] Move the screenshot script in docker
- [ ] Regex to isolate hyperlinks from screenshots
- [ ] Remove past screenshots
- [ ] Remove history
- [ ] Expand linux support
- [x] Windows support
- [ ] macos support
- [ ] Improve search algorithm (use embeddings combined with fuzzy search)
- [ ] Add LLM chat support (eg: be able to ask "how much time have I been working on my IDE today?")
