# Crawl4AI CLI Tests

Tests for the `crwl` CLI commands documented in SKILL.md.

## Running Tests

```bash
./test_cli.sh
```

## Test Coverage

| Test | Description |
|------|-------------|
| Basic markdown | `crwl crawl -o md` returns content |
| JSON output | `crwl crawl -o json` returns valid JSON |
| File output | `-O file.md` creates file with content |
| Cache bypass | `-bc` flag works |
| Verbose mode | `-v` flag works |
| JS-rendered | JavaScript-heavy site returns content |

## Requirements

- `crwl` CLI installed (`uv tool install 'crawl4ai[all]' && crawl4ai-setup`)
- Network access to test URLs
