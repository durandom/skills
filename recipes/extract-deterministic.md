# Recipe: Extracting Deterministic Work from AI Workflows

**Target Audience:** Developers reviewing AI conversations, skills, and prompts
**Goal:** Identify work that should be deterministic scripts instead of repeated AI prompts

---

## Foundational Principle

### The Core Heuristic

**Will you need the same result twice?** → Write a script.

AI is non-deterministic. Using it for deterministic work (counting, parsing, exact operations, repeatable tasks) produces unreliable results and wastes tokens.

**Don't ask AI to do deterministic work. Ask AI to write code that does it.**

| Task Type | AI Prompt | Script |
|-----------|-----------|--------|
| **Repetition needed** | ✗ | ✓ |
| **Exact output required** | ✗ | ✓ |
| **Counting/parsing** | ✗ | ✓ |
| **Variance acceptable** | ✓ | ✗ |
| **Judgment required** | ✓ | ✗ |

### The One-Liner Test

> *"If I asked AI this again tomorrow, would I be annoyed if the output differed?"*

**Yes** → Extract to script. **No** → AI prompt is fine.

---

## Detection Signals

### In Conversations

Look for these patterns when reviewing chat logs:

#### Signal 1: Repetition Markers

Keywords and phrases that indicate repeated requests:

```
"do this again"
"same as before"
"like last time"
"every time I..."
"I keep asking you to..."
"can you do that for the other files too"
```

**Example conversation smell:**

```
User: Count the TODO comments in src/
AI: I found 23 TODO comments...

[3 days later]

User: Count the TODO comments in src/ again
AI: I found 27 TODO comments...
```

**Extraction opportunity:** `grep -r "TODO" src/ | wc -l`

#### Signal 2: Exact Format Requirements

Phrases indicating precise output needs:

```
"exactly like this"
"format it as..."
"always use this structure"
"must be in this format"
"with exactly N decimal places"
"in ISO 8601 format"
```

**Example conversation smell:**

```
User: Convert this date to ISO 8601 format
AI: 2024-03-15T10:30:00Z

User: And this one too, same format
AI: 2024-03-16T14:45:00Z
```

**Extraction opportunity:** `date -d "$input" -Iseconds`

#### Signal 3: Counting and Enumeration

Requests involving quantities:

```
"how many..."
"count the..."
"list all..."
"find every..."
"what's the total..."
```

**Example conversation smell:**

```
User: How many lines of code in this project?
AI: Approximately 15,000 lines...
```

**Red flag:** "Approximately" — AI is guessing, not counting.

**Extraction opportunity:** `find . -name "*.py" | xargs wc -l`

#### Signal 4: Data Transformation Pipelines

Multi-step transformations described in prose:

```
"take this and convert it to..."
"extract X, then format as Y"
"parse this and output as..."
"transform each item by..."
```

**Example conversation smell:**

```
User: Take this CSV, extract the email column,
      deduplicate, sort alphabetically,
      and output one per line
```

**Extraction opportunity:**

```bash
cut -d',' -f3 input.csv | sort -u
```

#### Signal 5: Validation Requests

Checking conformance to rules:

```
"check if this is valid"
"does this match the pattern"
"verify the format"
"validate against..."
```

**Example conversation smell:**

```
User: Check if all these URLs are valid
AI: Let me check each one...
    - https://example.com ✓
    - htp://bad.url ✗ (protocol typo)
```

**Extraction opportunity:**

```bash
while read url; do
  curl -s -o /dev/null -w "%{http_code} $url\n" "$url"
done < urls.txt
```

### In Skills, Prompts, and Commands

Look for these patterns when reviewing reusable AI instructions:

#### Signal 6: Hardcoded Transformation Steps

Instructions that describe exact algorithms:

```markdown
# BAD: Algorithm described in prose
When processing the file:
1. Remove all blank lines
2. Sort alphabetically
3. Remove duplicates
4. Add line numbers
```

**Extraction opportunity:** `grep -v '^$' | sort -u | nl`

#### Signal 7: Format Templates

Output structures defined in the prompt:

```markdown
# BAD: Template in prompt
Always output in this exact format:
---
Title: {title}
Date: {date}
Tags: {comma-separated tags}
---
```

**Extraction opportunity:** Script that generates the frontmatter from inputs.

#### Signal 8: Conditional Logic Trees

Decision trees that could be code:

```markdown
# BAD: Business logic in prose
If the file is a test file (ends in _test.py):
  - Add to test manifest
  - Skip coverage check
If the file is in /vendor/:
  - Skip entirely
Otherwise:
  - Run linter
  - Check formatting
```

**Extraction opportunity:** Shell script with actual conditionals.

#### Signal 9: Regular Expression Descriptions

Patterns described in words:

```markdown
# BAD: Regex described in English
Find all strings that start with "API_"
followed by uppercase letters and underscores
```

**Extraction opportunity:** `grep -E 'API_[A-Z_]+'`

#### Signal 10: File System Operations

Bulk operations on files:

```markdown
# BAD: File ops in prompt
Find all PNG files larger than 1MB,
move them to /archive/,
and create a manifest of what was moved
```

**Extraction opportunity:**

```bash
find . -name "*.png" -size +1M -exec mv {} /archive/ \; \
  -print > manifest.txt
```

---

## Extraction Patterns

Once you've detected an opportunity, follow these patterns to extract:

### Pattern 1: The Prototype Loop

1. Ask AI to write the script (not do the task)
2. Test the script on sample input
3. Fix edge cases (ask AI to help debug)
4. Commit the working script
5. Run the script whenever needed

```
# Instead of:
User: Count the TODO comments in my codebase

# Do:
User: Write a bash script that counts TODO comments,
      broken down by directory
```

### Pattern 2: Conversation Mining

Review past conversations for extraction opportunities:

```bash
# Questions to ask when reviewing:
# 1. Did I ask similar things multiple times?
# 2. Did I need exact/consistent output?
# 3. Did AI say "approximately" or vary between runs?
# 4. Did I describe a multi-step transformation?
```

For each "yes", consider extraction.

### Pattern 3: Prompt Refactoring

Transform prompt instructions into script calls:

```markdown
# BEFORE (in prompt):
When the user provides a URL, fetch it and extract:
- Page title
- Meta description
- All h1 headings
Format as JSON.

# AFTER (in prompt):
When the user provides a URL, run:
`./scripts/extract_meta.sh <url>`
And present the JSON output.
```

### Pattern 4: Validation Extraction

Move validation rules from prose to code:

```markdown
# BEFORE (in prompt):
Check that the commit message:
- Starts with a type (feat/fix/docs/etc)
- Has a colon after the type
- Is under 72 characters
- Doesn't end with a period

# AFTER (prompt + script):
Run `./scripts/validate_commit.sh "$message"`
If it fails, show the user the error output.
```

```bash
#!/bin/bash
# validate_commit.sh
msg="$1"
[[ "$msg" =~ ^(feat|fix|docs|style|refactor|test|chore): ]] ||
  { echo "Error: Must start with type:"; exit 1; }
[[ ${#msg} -le 72 ]] ||
  { echo "Error: Must be ≤72 chars"; exit 1; }
[[ "$msg" != *. ]] ||
  { echo "Error: No trailing period"; exit 1; }
echo "Valid"
```

### Pattern 5: Template Extraction

Move output templates to actual template files:

```markdown
# BEFORE (in prompt):
Generate a changelog entry in this format:
## [version] - YYYY-MM-DD
### Added
- item
### Fixed
- item

# AFTER (template file + prompt):
Use the template in ./templates/changelog.md
Fill in the placeholders based on the git log.
```

---

## Review Checklists

### Conversation Audit Checklist

Use when reviewing a completed conversation:

```
□ Any request made more than once?
□ Any "count", "list", or "find all" requests?
□ Any exact format requirements specified?
□ Any multi-step transformations described?
□ Did AI output include "approximately" or vary?
□ Any validation or checking requests?
□ Any file system bulk operations?

→ Each "yes" = potential extraction opportunity
```

### Skill/Prompt Audit Checklist

Use when reviewing a skill or system prompt:

```
□ Does it describe an algorithm step-by-step?
□ Does it include output format templates?
□ Does it contain conditional logic trees?
□ Does it describe regex patterns in English?
□ Does it specify validation rules?
□ Does it include file/data transformation steps?
□ Could any section be replaced with "run this script"?

→ Each "yes" = potential extraction opportunity
```

### Quick Triage Matrix

| If you see... | Confidence | Action |
|---------------|------------|--------|
| "count/list/find all" | High | Extract immediately |
| "same format as before" | High | Extract immediately |
| "approximately" in AI output | High | Extract immediately |
| Multi-step transformation | Medium | Evaluate complexity |
| Validation rules in prose | Medium | Extract if >2 rules |
| One-time data question | Low | Probably fine as-is |
| Judgment/opinion request | Low | Keep as AI task |

---

## Examples

### Example 1: Log Analysis

**Before (conversation):**

```
User: How many ERROR lines in today's log?
AI: I count 47 ERROR lines in the log...

[Next day]
User: How many ERROR lines in today's log?
AI: I see 52 ERROR lines...
```

**After (script):**

```bash
#!/bin/bash
# count_errors.sh
log_file="${1:-/var/log/app.log}"
grep -c "ERROR" "$log_file"
```

**Usage:** `./count_errors.sh` — instant, reliable, same every time.

---

### Example 2: Code Generation Template

**Before (in skill prompt):**

```markdown
When creating a new React component:
1. Create ComponentName.tsx with this structure:
   - Import React
   - Define Props interface
   - Export default function component
   - Include basic JSX wrapper
2. Create ComponentName.test.tsx with:
   - Import testing-library
   - Basic render test
3. Create index.ts that re-exports the component
```

**After (script + simplified prompt):**

```bash
#!/bin/bash
# new_component.sh
name="$1"
mkdir -p "src/components/$name"

cat > "src/components/$name/$name.tsx" << 'EOF'
import React from 'react';

interface Props {}

export default function $name({}: Props) {
  return <div>$name</div>;
}
EOF

# ... similar for test and index files
```

**New prompt:** `Run ./scripts/new_component.sh <name>`

---

### Example 3: PR Description Extraction

**Before (conversation):**

```
User: Summarize the changes in this PR for the description.
      Include: files changed, type of change, testing notes.
```

**After (script + AI combo):**

```bash
#!/bin/bash
# pr_context.sh - Gather deterministic facts
echo "## Files Changed"
git diff --stat main...HEAD

echo "## Commits"
git log --oneline main...HEAD

echo "## Test Files Modified"
git diff --name-only main...HEAD | grep -E '_test\.|\.test\.'
```

**New prompt:**

```
Run ./scripts/pr_context.sh and use the output to write
a PR description. Add your judgment on risk level and
suggested reviewers.
```

**Key insight:** Script gathers facts (deterministic). AI adds judgment (non-deterministic). Each does what it's good at.

---

### Example 4: Dependency Audit

**Before (repeated conversation):**

```
User: Check which of my npm dependencies have known vulnerabilities
AI: Let me analyze your package.json...
    - lodash: CVE-2021-23337 (high severity)
    - axios: no known issues
    ...
```

**Problem:** AI may hallucinate CVEs or miss recent ones.

**After (script):**

```bash
#!/bin/bash
# audit_deps.sh
npm audit --json | jq '.vulnerabilities | to_entries[] |
  {name: .key, severity: .value.severity, via: .value.via[0]}'
```

**AI's new role:** Explain the vulnerabilities, suggest fixes, prioritize remediation — judgment tasks.

---

## Anti-Patterns

### Anti-Pattern 1: Asking AI to Count

```
# BAD: AI is unreliable at counting
User: How many functions are in this file?
AI: There are approximately 12 functions...

# GOOD: Script counts, AI explains
User: Run `grep -c "^def " file.py` and tell me
      which functions might be candidates for refactoring
```

### Anti-Pattern 2: Repeated Format Requests

```
# BAD: Asking AI to format the same way repeatedly
User: Format this as a markdown table
[... 10 messages later ...]
User: Format this as a markdown table too

# GOOD: Script for the transformation
./scripts/csv_to_md_table.sh input.csv
```

### Anti-Pattern 3: Prose Algorithms in Prompts

```markdown
# BAD: Algorithm that should be code
To process user uploads:
- If image: resize to max 1200px width
- If PDF: extract first page as thumbnail
- If video: reject with error message
- Calculate SHA256 hash for deduplication

# GOOD: Script handles the logic
Run `./scripts/process_upload.sh <file>` which handles
file type detection, processing, and returns JSON result.
Report any errors to the user with suggestions.
```

### Anti-Pattern 4: Validation by Vibes

```markdown
# BAD: AI validates by interpretation
Check if this JSON is valid and well-formed.

# GOOD: Tool validates, AI explains errors
Run `jq . < input.json`. If it fails, explain the error
to the user and suggest how to fix it.
```

### Anti-Pattern 5: Leaving Extraction for Later

```
# BAD: "I'll extract this eventually"
# (You won't. Extract on second occurrence.)

# GOOD: Second time you need it = extraction time
# First ask: AI does it
# Second ask: AI writes the script
```

---

## Decision Flowchart

```
                    ┌─────────────────────┐
                    │ New task from user  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Will I need exact   │
                    │ same result again?  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │ YES            │ MAYBE          │ NO
              ▼                ▼                ▼
        ┌───────────┐   ┌───────────────┐  ┌──────────┐
        │ Extract   │   │ AI does it    │  │ AI does  │
        │ to script │   │ this time.    │  │ it once  │
        │ now       │   │ Track for     │  │          │
        └───────────┘   │ next request  │  └──────────┘
                        └───────────────┘

        ┌─────────────────────────────────┐
        │ Is the task about:              │
        │ • Counting/measuring            │
        │ • Parsing/extracting            │
        │ • Format transformation         │
        │ • Validation against rules      │
        │ • File system bulk operations   │
        └────────────────┬────────────────┘
                         │
           ┌─────────────┼─────────────┐
           │ YES         │             │ NO
           ▼             │             ▼
     ┌───────────┐       │       ┌───────────────┐
     │ EXTRACT   │       │       │ Judgment,     │
     │ (AI bad   │       │       │ creativity,   │
     │ at this)  │       │       │ explanation   │
     └───────────┘       │       │ → AI is fine  │
                         │       └───────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Still       │
                  │ unsure?     │
                  │ Do it with  │
                  │ AI once.    │
                  │ If repeated │
                  │ → extract   │
                  └─────────────┘
```

---

## Summary

| Signal | Detection | Extraction |
|--------|-----------|------------|
| **Repetition** | "again", "same as", "like before" | Script the operation |
| **Exact format** | "exactly", "must be", "always" | Template + script |
| **Counting** | "how many", "count", "total" | grep/wc/find pipeline |
| **Parsing** | "extract", "parse", "pull out" | awk/sed/jq script |
| **Transformation** | "convert", "transform", "format as" | Data pipeline script |
| **Validation** | "check", "verify", "valid" | Validation script |
| **Bulk file ops** | "all files", "each file", "move/copy" | find + xargs script |

### The Golden Rule

> **AI figures out the tricky bits once. Code runs them reliably forever.**

Use AI to explore, prototype, and handle edge cases during script creation.
Use scripts for everything that needs to produce the same result twice.

---

## References

- [Offload Deterministic Pattern](https://github.com/lexler/augmented-coding-patterns/blob/main/documents/patterns/offload-deterministic.md)
- [Non-Determinism Obstacle](https://github.com/lexler/augmented-coding-patterns/blob/main/documents/obstacles/non-determinism.md)
- [Knowledge Checkpoint Pattern](https://github.com/lexler/augmented-coding-patterns/blob/main/documents/patterns/knowledge-checkpoint.md)
