#!/bin/sh

# Get clipboard entries from API
entries=$(curl -s http://127.0.0.1:8000/clipboard | jq -r '.entries[] | "\(.timestamp) | \(.caller.hostname) | \(.content)"')

# Show entries in Rofi and get selection
selected=$(echo "$entries" | rofi -dmenu -i -p "Clipboard History" -theme-str 'window {width: 80%;} listview {lines: 10;}')

# Extract content from selection and copy to system clipboard
if [ -n "$selected" ]; then
    content=$(echo "$selected" | awk -F' | ' '{print $NF}')
    echo -n "$content" | xclip -selection clipboard
    notify-send "Clipboard" "Content copied to clipboard"
fi
