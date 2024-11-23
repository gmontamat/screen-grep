#!/bin/bash

# Define output directory
OUTPUT_DIR=${OUTPUT_DIR:-data/screenshots}
# Create the directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"
# Get the interval from the first argument or 5 seconds
interval=${1:-5}

take_screenshot() {
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    FILENAME="$OUTPUT_DIR/screenshot_$TIMESTAMP.png"

    if [ "$XDG_SESSION_DESKTOP" = "KDE" ]; then
        # For KDE Plasma using Spectacle
        spectacle -b -a -n -o "$FILENAME"
    elif [ "$XDG_SESSION_TYPE" = "x11" ]; then
        # For X11 using xdotool and import
        WINDOW_ID=$(xdotool getactivewindow)
        import -window "$WINDOW_ID" "$FILENAME"
    elif [ "$XDG_SESSION_TYPE" = "wayland" ]; then
        # For Wayland, assuming grim is installed
        grim -g "$(swaymsg -t get_tree | jq -r '.. | select(.type?) | select(.focused==true).rect | "(.x),(.y) (.width)x(.height)"')" "$FILENAME"
    elif [ "$(uname)" = "Darwin" ]; then
        # For macOS using screencapture (WIP: this captures main screen when "Displays have separate Spaces" is off)
        screencapture -x "$FILENAME"
    else
        echo "Unsupported session type or desktop environment."
    fi
}

while true; do
  take_screenshot
  sleep "$interval"
done
