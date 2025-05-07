#!/bin/sh
# Get clipboard entries from API, using Tab separator and JSON encoding for content
entries=$(curl -sf http://192.168.1.125:8000/clipboard | \
          jq -r '.entries[] | "\(.timestamp)\t\(.caller.hostname)\t\(.content | @json)"')
# Check if curl or jq failed
if [ $? -ne 0 ]; then
    notify-send -u critical "Clipboard Error" "Failed to fetch or parse clipboard data."
    exit 1
fi
# Handle empty entries
if [ -z "$entries" ]; then
    rofi -e "Clipboard history is empty."
    exit 0
fi
# Show entries in Rofi and get selection
# Now using system-wide config for key bindings, no need to specify them here
selected=$(echo "$entries" | rofi -dmenu -i -p "Clipboard History")
# Extract content from selection and copy to system clipboard
if [ -n "$selected" ]; then
    # Use cut to get the JSON-encoded string part (field 3 onwards)
    json_encoded_content=$(echo "$selected" | cut -f3- -d$'\t')
    # Use jq to decode the JSON string back into the raw content
    # The -r flag removes the outer quotes from the resulting string
    content=$(echo "$json_encoded_content" | jq -r '.')
    # Copy the exact content to the clipboard
    echo -n "$content" | xclip -selection clipboard
    notify-send "Clipboard" "Content copied to clipboard"
fi
