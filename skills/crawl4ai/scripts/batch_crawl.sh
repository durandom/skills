#!/bin/bash
# Crawl4AI Batch Processor
# Usage: ./batch_crawl.sh urls.txt [output_dir]
#
# Process multiple URLs from a file, saving markdown output for each.
# Lines starting with # are treated as comments.

set -e

URLS_FILE="${1:-urls.txt}"
OUTPUT_DIR="${2:-output}"

if [[ ! -f "$URLS_FILE" ]]; then
    echo "Usage: $0 <urls_file> [output_dir]"
    echo ""
    echo "Example urls.txt:"
    echo "  https://example.com"
    echo "  https://docs.example.com"
    echo "  # This is a comment"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

success=0
failed=0

while IFS= read -r url || [[ -n "$url" ]]; do
    # Skip comments and empty lines
    [[ "$url" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${url// }" ]] && continue

    # Create safe filename from URL
    filename=$(echo "$url" | sed 's|https\?://||; s|/|_|g; s|[^a-zA-Z0-9_.-]|_|g' | cut -c1-100)

    echo "Crawling: $url"

    if crwl crawl -o md -O "$OUTPUT_DIR/${filename}.md" "$url" 2>/dev/null; then
        echo "  ✅ Saved: $OUTPUT_DIR/${filename}.md"
        ((success++))
    else
        echo "  ❌ Failed: $url"
        ((failed++))
    fi
done < "$URLS_FILE"

echo ""
echo "Batch crawl complete:"
echo "  ✅ Success: $success"
echo "  ❌ Failed:  $failed"
echo "  📁 Output:  $OUTPUT_DIR/"
