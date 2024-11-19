FROM debian:latest

RUN apt-get update && \
    apt-get install -y \
    xdotool \
    imagemagick \
    jq \
    grim \
    sway \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD screenshot.sh .

RUN chmod +x /app/screenshot.sh

ENTRYPOINT ["/app/screenshot.sh", "5"]
