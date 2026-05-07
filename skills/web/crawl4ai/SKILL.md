---
name: crawl4ai
description: Web crawling and data extraction using the crwl CLI. Use this skill when users need to scrape websites, extract markdown content, handle JavaScript-heavy pages, or extract structured data from web pages.
metadata:
  version: "1.0.0"
  crawl4ai_cli: crwl
  last_updated: "2025-01-19"
---

<objective>
Extract web content as clean markdown using the `crwl` CLI. This skill handles static sites, JavaScript-rendered SPAs, and structured data extraction without requiring Python code.

**Primary use cases:**

- Convert documentation sites to markdown
- Scrape JavaScript-heavy pages (React, Vue, Obsidian Publish)
- Extract structured data from e-commerce, news, or catalog sites
- Batch process multiple URLs
</objective>

<quick_start>
**Basic crawl:**

```bash
crwl crawl -o md https://example.com
```

**Save to file:**

```bash
crwl crawl -o md -O output.md https://example.com
```

**JavaScript-heavy site (use pre-made config):**

```bash
crwl crawl -C configs/spa.yaml -bc -o md "https://spa-site.com"
```

</quick_start>

<installation>
```bash
# Using uv (recommended) - include [all] for ML features
uv tool install 'crawl4ai[all]'

# Or with pip

pip install 'crawl4ai[all]'

# Run setup after installation

crawl4ai-setup

# Verify installation

crwl --help
crawl4ai-doctor

```

> **Note:** The `[all]` extra is required for ML features. Without it, `crawl4ai-download-models` will fail.
</installation>

<core_commands>
**Markdown extraction:**
```bash
crwl crawl -o md https://docs.example.com           # Basic
crwl crawl -o md-fit https://docs.example.com       # Filtered (removes boilerplate)
crwl crawl -o md -O docs.md https://docs.example.com  # Save to file
```

**Structured data extraction:**

```bash
crwl crawl -j "extract product names and prices" https://shop.com  # LLM-based
crwl crawl -s schema.json https://shop.com                          # Schema-based (faster)
```

**Deep crawling:**

```bash
crwl crawl --deep-crawl bfs --max-pages 10 https://docs.example.com  # Breadth-first
crwl crawl --deep-crawl dfs --max-pages 5 https://blog.example.com   # Depth-first
```

**Question answering:**

```bash
crwl crawl -q "What are the main features?" https://product.example.com
```

</core_commands>

<spa_handling>
**Critical pattern for JavaScript-heavy sites (React, Vue, Obsidian Publish, etc.):**

CSS selectors alone don't work—the element exists but content loads asynchronously. Use a **JS wait condition** that checks for actual rendered text.

**Use the pre-made SPA config:**

```bash
crwl crawl -C configs/spa.yaml -bc -o md "https://spa-site.com"
```

**Or create a site-specific config:**

```yaml
# my_site_config.yaml
page_timeout: 60000
wait_for: "js:() => document.body.innerText.includes('expected content')"
```

```bash
crwl crawl -C my_site_config.yaml -bc -o md "https://my-spa-site.com"
```

**Why `-bc` (bypass cache)?** SPA content can be cached before JS renders. Always use `-bc` for SPAs.
</spa_handling>

<configs>
**Pre-made configs in `configs/` folder:**

| Config | Use Case |
|--------|----------|
| `spa.yaml` | Generic SPA (waits for content length > 1000) |
| `obsidian-publish.yaml` | Obsidian Publish sites |
| `slow-site.yaml` | Sites with slow loading (60s timeout) |

**Example usage:**

```bash
# Obsidian Publish site
crwl crawl -C configs/obsidian-publish.yaml -bc -o md "https://plugins.javalent.com/statblocks/readme/bestiary"

# Generic SPA
crwl crawl -C configs/spa.yaml -bc -o md "https://react-app.example.com"
```

</configs>

<output_formats>

| Format | Flag | Description |
|--------|------|-------------|
| Markdown | `-o md` | Clean markdown |
| Filtered markdown | `-o md-fit` | Removes navigation, ads, boilerplate |
| JSON | `-o json` | Full JSON with metadata, links, media |
| All | `-o all` | Everything (default) |

</output_formats>

<parameters>
**Crawler parameters (`-c`):**
```bash
crwl crawl -c wait_for=css:.content URL           # Wait for element
crwl crawl -c page_timeout=60000 URL              # Extended timeout (ms)
crwl crawl -c remove_overlay_elements=true URL    # Remove popups
```

**Browser parameters (`-b`):**

```bash
crwl crawl -b viewport_width=1920,viewport_height=1080 URL  # Custom viewport
crwl crawl -b user_agent="Mozilla/5.0..." URL               # Custom user agent
```

**Config files (`-C`, `-B`):**

```bash
crwl crawl -C crawler_config.yaml URL   # Crawler config
crwl crawl -B browser_config.yaml URL   # Browser config
```

</parameters>

<schema_extraction>
**Example schema.json for structured extraction:**

```json
{
  "name": "products",
  "baseSelector": "div.product",
  "fields": [
    {"name": "title", "selector": "h2", "type": "text"},
    {"name": "price", "selector": ".price", "type": "text"},
    {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
  ]
}
```

**Usage:**

```bash
crwl crawl -s schema.json https://shop.com
```

</schema_extraction>

<batch_processing>
For multiple URLs, use the provided script.

Script paths are **relative to this SKILL.md file** (not the working directory).
Derive the absolute script path from this file's location:

- If this SKILL.md is at `/path/to/crawl4ai/SKILL.md`
- Then the script is at `/path/to/crawl4ai/scripts/batch_crawl.sh`
- And configs are at `/path/to/crawl4ai/configs/`

```bash
scripts/batch_crawl.sh urls.txt output_dir
```

**Or inline:**

```bash
while read url; do
  crwl crawl -o md -O "output/$(echo $url | sed 's|https://||;s|/|_|g').md" "$url"
done < urls.txt
```

</batch_processing>

<troubleshooting>
<problem name="js_not_loading">
**Symptom:** Getting navigation/skeleton but no content

**Solution:** Use SPA config with JS wait condition:

```bash
crwl crawl -C configs/spa.yaml -bc -o md URL
```

If still failing, create site-specific config:

```yaml
page_timeout: 60000
wait_for: "js:() => document.body.innerText.includes('expected text')"
```

</problem>

<problem name="bot_detection">
**Symptom:** Empty response or access denied

**Solution:** Use realistic browser settings:

```bash
crwl crawl \
  -b viewport_width=1920,viewport_height=1080 \
  -b user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  URL
```

</problem>

<problem name="empty_content">
**Symptom:** Minimal or no content extracted

**Solution:** Check with verbose mode, then try waiting for content:

```bash
crwl crawl -v URL
crwl crawl -c wait_for=css:main URL
```

</problem>
</troubleshooting>

<cli_reference>

```
crwl crawl [OPTIONS] URL

Options:
  -o, --output [md|md-fit|json|all]    Output format
  -O, --output-file PATH               Save to file
  -C, --crawler-config PATH            Crawler config file (YAML/JSON)
  -B, --browser-config PATH            Browser config file (YAML/JSON)
  -s, --schema PATH                    JSON schema for extraction
  -j, --json-extract TEXT              LLM extraction instruction
  -q, --question TEXT                  Ask question about content
  -c, --crawler TEXT                   Crawler params (key=value)
  -b, --browser TEXT                   Browser params (key=value)
  -bc, --bypass-cache                  Skip cache
  --deep-crawl [bfs|dfs|best-first]    Multi-page crawling
  --max-pages INTEGER                  Max pages for deep crawl
  -v, --verbose                        Verbose output
  -h, --help                           Show help
```

</cli_reference>

<resources>
**configs/** - Pre-made crawler configs for common patterns
**scripts/** - `batch_crawl.sh` for processing multiple URLs
</resources>

<success_criteria>
Crawl is successful when:

- Output contains the actual page content (not just navigation/skeleton)
- For SPAs: body text includes expected content, not "Not found" or empty
- Markdown is clean and readable
- Structured extraction returns expected fields

**Quick validation:**

```bash
# Should return actual content, not just nav elements
crwl crawl -C configs/spa.yaml -bc -o md URL | head -50
```

</success_criteria>
