# Script Design for Agent Use

When to bundle scripts, how to structure them, and what makes a script agent-friendly.

Source: agentskills `using-scripts.mdx` + production patterns.

---

## When to Bundle a Script

Bundle a script in `scripts/` when:
- The same code runs across multiple invocations (deploy, setup, API calls)
- The operation is error-prone if rewritten from scratch each time
- Multiple test case runs in `skill-creator` evals all independently wrote the same helper script
- A one-off command has grown complex enough to be unreliable in a code block

**Don't bundle** for simple one-off commands — reference them directly in SKILL.md:

```markdown
Run the linter:
```bash
uvx ruff@0.8.0 check .
```
```

Use `uvx`, `npx`, `bunx`, or `go run` for package-level tools — they handle deps and versioning without requiring a `scripts/` directory.

---

## Referencing Scripts from SKILL.md

Use **relative paths from the skill directory root**:

```markdown
## Available scripts

- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data and writes `results.json`

## Workflow

1. Run validation:
   ```bash
   bash scripts/validate.sh "$INPUT_FILE"
   ```

2. Process results:
   ```bash
   uv run scripts/process.py --input results.json
   ```
```

**Path resolution note:** Script paths in SKILL.md are relative to the skill directory, not the working directory. If your skill is installed in a plugin cache far from the project, use `${CLAUDE_SKILL_DIR}` to derive the absolute path:

```bash
SCRIPT="${CLAUDE_SKILL_DIR}/scripts/process.py"
uv run "$SCRIPT" --input results.json
```

Or add this note in SKILL.md:
> Script paths are relative to this SKILL.md file. If SKILL.md is at `/path/to/skill/SKILL.md`, the script is at `/path/to/skill/scripts/process.py`.

---

## Self-Contained Scripts (Inline Dependencies)

Python with PEP 723 (recommended):

```python
# scripts/extract.py
# /// script
# dependencies = [
#   "beautifulsoup4>=4.12,<5",
# ]
# ///

from bs4 import BeautifulSoup
# ...
```

Run with:
```bash
uv run scripts/extract.py input.html
```

`uv run` creates an isolated environment, installs deps, and runs the script. No separate `pip install` step needed.

---

## Designing Scripts for Agents

When an agent runs your script, it reads stdout/stderr to decide what to do next. These design choices matter:

### No Interactive Prompts (Hard Requirement)

Agents run in non-interactive shells. Any TTY prompt or confirmation dialog will hang indefinitely.

```bash
# BAD: hangs
$ python scripts/deploy.py
Target environment: _

# GOOD: clear error
$ python scripts/deploy.py
Error: --env is required. Options: development, staging, production.
Usage: python scripts/deploy.py --env staging --tag v1.2.3
```

Accept all input via flags, environment variables, or stdin.

### Document with `--help`

`--help` output is the primary way an agent learns your script's interface.

```
Usage: scripts/process.py [OPTIONS] INPUT_FILE

Process input data and produce a summary report.

Options:
  --format FORMAT    Output format: json, csv, table (default: json)
  --output FILE      Write output to FILE instead of stdout
  --verbose          Print progress to stderr

Examples:
  scripts/process.py data.csv
  scripts/process.py --format csv --output report.csv data.csv
```

Keep it concise — it enters the context window.

### Write Helpful Error Messages

```
Error: --format must be one of: json, csv, table.
       Received: "xml"
```

Say what went wrong, what was expected, and what to try.

### Use Structured Output

Prefer JSON, CSV, or TSV over free-form text. Structured output is composable with `jq`, `cut`, etc.

Separate data from diagnostics:
- **stdout** — structured data the agent consumes
- **stderr** — progress messages, warnings, diagnostics

### Further Considerations

- **Idempotency** — Agents may retry. "Create if not exists" > "create and fail on duplicate."
- **Dry-run flag** — `--dry-run` for destructive operations lets the agent preview safely.
- **Meaningful exit codes** — Document exit codes in `--help` (0 = success, 1 = not found, 2 = invalid args, etc.)
- **Output size** — Many agent harnesses truncate at 10-30K chars. If your script may produce large output, default to a summary and support `--offset` or `--output FILE` for full results.
- **Explicit confirmation flags** — For destructive operations, require `--confirm` or `--force` rather than relying on `--dry-run` alone.

---

## Checklist Before Shipping a Script

- [ ] No interactive prompts
- [ ] `--help` output is clear and complete
- [ ] Error messages say what failed and how to fix it
- [ ] Structured output (JSON/CSV) for data, stderr for diagnostics
- [ ] Idempotent — safe to retry
- [ ] Inline dependencies (PEP 723 for Python, `npm:` for Deno/Bun)
- [ ] Documented in SKILL.md with script path and purpose
- [ ] Path resolution explained (relative to SKILL.md / `${CLAUDE_SKILL_DIR}`)
