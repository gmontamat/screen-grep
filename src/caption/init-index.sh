#!/bin/bash

ES_HOST=${ES_HOST:-localhost}

# Wait for Elasticsearch to start
until curl -s "http://$ES_HOST:9200"; do
  echo "Waiting for Elasticsearch..."
  sleep 5
done

# Check if the index already exists
if curl -s -o /dev/null -w "%{http_code}" "http://$ES_HOST:9200/screenshots" | grep -q "200"; then
  echo "Index 'screenshots' already exists."
  exit 0
fi

# Create the index with mapping
curl -X PUT "http://$ES_HOST:9200/screenshots" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "image_path": { "type": "keyword" },
      "caption": { "type": "text" },
      "ocr": { "type": "text" }
    }
  }
}'
