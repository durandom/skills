#!/bin/bash
# CLI tests for crawl4ai skill
# Verifies that crwl commands from SKILL.md work correctly

set -e

PASS=0
FAIL=0

test_pass() {
    echo "  ✅ $1"
    ((PASS++))
}

test_fail() {
    echo "  ❌ $1"
    ((FAIL++))
}

echo "=== Crawl4AI CLI Tests ==="
echo ""

# Test 1: Basic markdown output
echo "Test 1: Basic markdown output"
if output=$(crwl crawl -o md https://example.com 2>&1); then
    if [[ "$output" == *"Example Domain"* ]]; then
        test_pass "Markdown contains expected content"
    else
        test_fail "Markdown missing expected content"
    fi
else
    test_fail "Command failed"
fi

# Test 2: JSON output
echo "Test 2: JSON output"
if output=$(crwl crawl -o json https://example.com 2>&1); then
    if [[ "$output" == *"\"url\":"* ]]; then
        test_pass "JSON contains url field"
    else
        test_fail "JSON missing url field"
    fi
else
    test_fail "Command failed"
fi

# Test 3: Output to file
echo "Test 3: Output to file"
tmpfile=$(mktemp)
if crwl crawl -o md -O "$tmpfile" https://example.com 2>&1; then
    if [[ -s "$tmpfile" ]]; then
        test_pass "File created with content"
    else
        test_fail "File empty"
    fi
else
    test_fail "Command failed"
fi
rm -f "$tmpfile"

# Test 4: Cache bypass
echo "Test 4: Cache bypass flag"
if crwl crawl -bc -o md https://example.com >/dev/null 2>&1; then
    test_pass "Cache bypass works"
else
    test_fail "Cache bypass failed"
fi

# Test 5: Verbose mode
echo "Test 5: Verbose mode"
if crwl crawl -v -o md https://example.com >/dev/null 2>&1; then
    test_pass "Verbose mode works"
else
    test_fail "Verbose mode failed"
fi

# Test 6: JS-heavy site (Obsidian plugin docs)
echo "Test 6: JavaScript-rendered content"
if output=$(crwl crawl -o md "https://plugins.javalent.com/statblocks/readme/bestiary" 2>&1); then
    if [[ -n "$output" ]]; then
        test_pass "JS-rendered page returns content"
    else
        test_fail "JS-rendered page empty"
    fi
else
    test_fail "Command failed"
fi

echo ""
echo "=== Results ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"

if [[ $FAIL -gt 0 ]]; then
    exit 1
fi
