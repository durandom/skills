# Recipe: Agentic CLI Design Patterns

**Target Audience:** AI Coding Agents (Claude, Gemini, Copilot)
**Goal:** Design CLI tools that are safe and effective when operated by AI agents.

---

## Foundational Principles

### Non-Interactive by Design

**AI agents cannot handle interactive prompts.** Every operation must be expressible as a single command with flags and arguments—no stdin prompts, no "Press y to continue", no interactive menus.

```
# BAD: Blocks waiting for input agent can't provide
$ cmd delete foo
Are you sure? [y/N]: _

# BAD: Interactive selection
$ cmd choose
Select an option:
  1) Option A
  2) Option B
> _

# GOOD: Everything via flags
$ cmd delete foo --confirm
$ cmd choose --option=A
```

**If confirmation is needed:** Use the dry-run pattern (Pattern 3) instead of prompts. The agent runs the preview, sees the result, then explicitly runs with `--force`.

### Capability Gradient

AI agents parse `--help` to understand available options. If destructive flags are visible, agents may use them immediately without understanding the consequences.

**Solution:** Create workflows where:

1. **Safe operations** are advertised in `--help`
2. **Destructive operations** are hidden and only revealed in command output
3. **Recovery paths** are provided when possible

This forces agents (and humans) to run the safe version first, see what would happen, then explicitly opt into the destructive action.

---

## Core Patterns

### Pattern 1: Sensible Defaults with Next-Step Hints

**Unix philosophy:** A command with no arguments should do something useful—ideally the most common safe operation—and then guide the user to related actions.

**Don't:** Show help or error when run without arguments (unless truly ambiguous).

**Do:** Execute the most common operation and provide breadcrumbs to other actions.

**Example output when running `cmd` with no arguments:**

```
$ cmd
Project Status
  3 items up to date
  1 item outdated (foo)
  2 items not tracked

Next steps:
  cmd sync          Sync outdated items
  cmd add <file>    Track new items
  cmd --help        Show all options
```

**Structure of every output:**

```
[Result of operation]

[Summary if applicable]

Next steps:
  cmd <most-likely-next>    Brief description
  cmd <second-option>       Brief description
  cmd --help                Show all options
```

**Why this matters for agents:**

1. Agents can explore by just running `cmd` — no need to parse `--help` first
2. Each output teaches the next logical action
3. Creates a natural "conversation" flow: run → see result → see what's next → run next

**Progressive complexity:**

| Invocation | Behavior |
|------------|----------|
| `cmd` | Most common safe action + hints |
| `cmd status` | Explicit status (same as default) |
| `cmd sync` | Next-level action (from hints) |
| `cmd sync --force` | Discovered via output of `cmd sync` |

**Anti-pattern:**

```
# BAD: Dumps help when no args
$ cmd
usage: cmd [-h] [--cleanup] [--sync] ...

# BAD: Errors without guidance
$ cmd
Error: No command specified
```

### Pattern 2: Hide Destructive Flags from Help

Define a `--force` flag that works but doesn't appear in `--help` output:

```
CLI Definition:
  --cleanup   "Find and remove stale items"    # Visible in help
  --force     HIDDEN                           # Functional but invisible
```

**Result of `--help`:**

```
options:
  --cleanup   Find and remove stale items
```

No `--force` visible. An AI agent will naturally try `--cleanup` first.

### Pattern 3: Dry-Run by Default (with Undo Hints)

Make the safe behavior the default. When `--cleanup` runs without `--force`:

```
function do_cleanup(items, execute):
    if items is empty:
        print "Nothing to clean up."
        return

    for each item in items:
        if execute:
            delete(item)
            print "  deleted: {item}"
        else:
            print "  would delete: {item}"

    if not execute:
        # Discovery path: reveal --force HERE
        print "This was a preview. Run with --force to delete."

        # Undo hint: if reversal is simple, show it
        if can_generate_undo_command(items):
            print "To restore after deletion: cmd restore {item_ids}"
```

**Key insight:** If undoing the operation is straightforward, include the undo command in the output. Don't over-engineer—only provide undo hints when the reversal is simple and deterministic.

### Pattern 4: Discovery Through Output

Reveal capabilities contextually. Different commands guide to different uses of `--force`:

```
# In check mode - guides to fixing drift
if drift_found:
    print "Run `cmd --force` to fix drift."

# In cleanup mode - guides to actual deletion
if stale_found:
    print "Run `cmd --cleanup --force` to remove them."
```

---

## Supporting Patterns

### Pattern 5: Verbose Mode for Agent Traceability

Provide a `--verbose` flag that logs every significant action. This allows agents to follow what's happening and debug failures:

```
CLI Definition:
  --verbose, -v   "Show detailed operation log"   # Visible in help
```

**Output with `--verbose`:**

```
$ cmd sync --verbose
[INFO] Connecting to remote...
[INFO] Fetching manifest (3 items)
[INFO] Comparing local state...
[INFO] Item 'foo' is outdated (local: v1, remote: v2)
[INFO] Item 'bar' is up to date
[INFO] Item 'baz' is missing locally
[RESULT] 1 outdated, 1 missing. Run with --force to sync.
```

Agents can parse these logs to understand what happened and why.

### Pattern 6: Machine-Readable Output (Optional)

For automation pipelines, offer structured output. Keep human-readable as the default:

```
CLI Definition:
  --json        "Output as JSON"                  # Visible in help
  --format      "Output format (text|json|yaml)"  # Alternative syntax
```

**Example:**

```
$ cmd status --json
{
  "items": [
    {"name": "foo", "status": "outdated", "local": "v1", "remote": "v2"},
    {"name": "bar", "status": "current"}
  ],
  "summary": {"outdated": 1, "current": 1}
}
```

**Note:** This is opt-in. Most agent interactions work fine with well-structured human-readable output.

### Pattern 7: Informative Error Messages

When things fail, provide actionable guidance. Agents need to know what went wrong and what to try next:

```
# Bad: Cryptic error
Error: Operation failed (code 7)

# Good: Informative error with next steps
Error: Cannot connect to server at api.example.com:443
  - Check network connectivity: ping api.example.com
  - Verify credentials: cmd auth status
  - Server status page: https://status.example.com
```

Include:

- **What failed** (specific, not generic)
- **Why it likely failed** (common causes)
- **What to try next** (concrete commands or URLs)

### Pattern 8: Scoped Permissions

Limit the blast radius of agent mistakes by supporting explicit permission boundaries:

```
CLI Definition:
  --allow-paths   "Restrict operations to these paths"   # Visible
  --deny-paths    "Exclude these paths from operations"  # Visible
```

**Example:**

```
$ cmd cleanup --allow-paths=/tmp,/var/cache
# Will only clean up items in /tmp and /var/cache
# Silently skips or errors on items outside these paths

$ cmd sync --deny-paths=/etc,/usr
# Will sync everything except /etc and /usr
```

This provides defense-in-depth when agents operate with broad file system access.

### Pattern 9: Trust Level Awareness

Consider categorizing operations by risk level. This helps frameworks and agents make decisions about what needs human approval:

**Conceptual categories:**

| Risk Level | Characteristics | Examples |
|------------|-----------------|----------|
| **Read-only** | No side effects | `status`, `list`, `diff` |
| **Reversible** | Can be undone | `stage`, `cache`, `bookmark` |
| **Destructive** | Permanent changes | `delete`, `force-push`, `drop` |
| **External** | Affects other systems | `deploy`, `publish`, `notify` |

Design your CLI so that:

- Read-only operations are the default behavior
- Destructive operations require explicit flags
- External operations clearly indicate their scope

### Pattern 10: Multi-Line Input Strategies

Agents often need to pass multi-line content (commit messages, code, configs). Since command-line arguments handle this poorly, support multiple input methods:

#### Method 1: File path argument (Recommended)

```bash
# Agent writes content to temp file, passes path
$ cmd create --file=/tmp/content.txt
$ cmd create -f /tmp/content.txt
```

```python
parser.add_argument("--file", "-f", type=argparse.FileType('r'),
                    help="Read content from file")
```

#### Method 2: Stdin with explicit flag

```bash
# Heredoc (works in most shells)
$ cmd create --stdin <<'EOF'
Line 1
Line 2
EOF

# Pipe from echo
$ echo "Line 1\nLine 2" | cmd create --stdin

# Convention: dash means stdin
$ cat content.txt | cmd create -f -
```

```python
parser.add_argument("--stdin", action="store_true",
                    help="Read content from stdin")

if args.stdin:
    content = sys.stdin.read()
elif args.file:
    content = args.file.read()
```

#### Method 3: Heredoc-friendly message flag

```bash
# For commit-message-style input
$ cmd commit -m "$(cat <<'EOF'
feat: Add new feature

This is a multi-line commit message
with detailed description.
EOF
)"
```

**Priority order for reading content:**

```python
def get_content(args):
    """Read content with clear precedence."""
    if args.file and args.file.name != '<stdin>':
        return args.file.read()
    if args.stdin or not sys.stdin.isatty():
        return sys.stdin.read()
    if args.message:
        return args.message
    return None
```

**Key points:**

- Always support `--file` for explicit file paths
- Use `--stdin` flag to explicitly request stdin reading
- The `-` convention (read from stdin) is widely understood
- Avoid auto-detecting stdin (can cause hangs if agent doesn't pipe anything)

### Pattern 11: Doctor/Validate

Provide a `doctor` or `validate` command that proactively diagnoses configuration, state, and environment issues. This is distinct from error handling (reactive) — doctor is **proactive health checking**.

```
CLI Definition:
  doctor        "Check configuration and environment health"   # Visible
  --fix         HIDDEN                                         # Auto-fix safe issues
```

**Output structure:**

```
$ cmd doctor
Checking configuration...

Errors (must fix):
  ✗ Config file missing: ~/.cmdrc
    → Run: cmd init

  ✗ Invalid API key format in $CMD_API_KEY
    → Check: echo $CMD_API_KEY | head -c 10

Warnings (should fix):
  ⚠ Cache directory is 2.3GB (recommend < 500MB)
    → Run: cmd cache prune

  ⚠ Using deprecated config key 'old_name' (use 'new_name')
    → Run: cmd doctor --fix (auto-migrates)

Info:
  ✓ Version: 2.1.0 (latest)
  ✓ Remote: connected (api.example.com)
  ✓ Auth: valid (expires in 29 days)

Summary: 2 errors, 2 warnings

Next steps:
  cmd init              Create missing config file
  cmd doctor --fix      Auto-fix 1 warning
  cmd doctor --verbose  Show all checks performed
```

**Issue categories:**

| Category | Symbol | Meaning | Auto-fixable? |
|----------|--------|---------|---------------|
| **Error** | ✗ | Blocking, must fix to proceed | Rarely |
| **Warning** | ⚠ | Non-blocking, should fix | Often |
| **Info** | ✓ | Healthy status | N/A |

**The `--fix` flag:**

Following Pattern 2 (hidden destructive flags), `--fix` is not shown in `--help`. It's revealed in doctor output only when auto-fixable issues exist:

```
$ cmd doctor --fix
Checking configuration...

Auto-fixing safe issues:
  ✓ Migrated config key 'old_name' → 'new_name'

Still need manual attention:
  ✗ Config file missing: ~/.cmdrc
    → Run: cmd init

Summary: 1 fixed, 1 error remaining

Next steps:
  cmd init        Create missing config file
  cmd doctor      Re-check after fixing
```

**What makes a good doctor check:**

1. **Environment** — required tools, versions, PATH entries
2. **Configuration** — file existence, syntax validity, deprecated keys
3. **State** — cache health, stale locks, orphaned temp files
4. **Connectivity** — API reachability, auth token validity
5. **Resources** — disk space, memory, file descriptor limits

**Integration with other patterns:**

- **Pattern 1 (Sensible Defaults):** Consider making `cmd` with no args run a lightweight health check
- **Pattern 5 (Verbose):** `cmd doctor --verbose` shows every check, not just failures
- **Pattern 6 (JSON):** `cmd doctor --json` for CI/automation pipelines
- **Pattern 7 (Errors):** When commands fail, suggest `cmd doctor` in error output

**Example implementation:**

```python
def do_doctor(args):
    """Run health checks and report issues."""
    checks = [
        check_config_file,
        check_api_key,
        check_cache_size,
        check_deprecated_keys,
        check_connectivity,
    ]

    errors, warnings, info = [], [], []

    for check in checks:
        result = check()
        if args.verbose or result.status != "ok":
            {
                "error": errors,
                "warning": warnings,
                "ok": info,
            }[result.status].append(result)

    # Display results...

    # Only show --fix hint if there are fixable issues
    fixable = [w for w in warnings if w.auto_fixable]
    if fixable and not args.fix:
        print(f"\nRun `cmd doctor --fix` to auto-fix {len(fixable)} issue(s)")

    if args.fix:
        for issue in fixable:
            issue.apply_fix()
            print(f"  ✓ {issue.fix_description}")

    return 1 if errors else 0
```

---

## Complete Example

```python
import argparse
import sys

def print_next_steps(hints):
    """Print next-step hints at the end of output."""
    print("\nNext steps:")
    for cmd, desc in hints:
        print(f"  {cmd:<20} {desc}")


def show_status(args):
    """Default action: show project status with next-step hints."""
    items = get_all_items()
    stale = [i for i in items if i.is_stale]
    current = [i for i in items if not i.is_stale]

    print("Project Status")
    print(f"  {len(current)} items up to date")
    if stale:
        print(f"  {len(stale)} items stale")

    # Context-aware hints based on current state
    hints = []
    if stale:
        hints.append(("cmd cleanup", "Preview stale item removal"))
    hints.append(("cmd sync", "Sync with remote"))
    hints.append(("cmd --help", "Show all options"))

    print_next_steps(hints)


def do_cleanup(args):
    """Cleanup with dry-run default and next-step hints."""
    stale_items = find_stale_items(args.allow_paths)

    if not stale_items:
        print("Nothing to clean up.")
        print_next_steps([
            ("cmd status", "Check project status"),
            ("cmd --help", "Show all options"),
        ])
        return 0

    for item in stale_items:
        if args.verbose:
            print(f"[INFO] Found stale: {item.path} (age: {item.age})")

        if args.force:
            delete(item)
            print(f"  deleted: {item.path}")
        else:
            print(f"  would delete: {item.path}")

    if args.force:
        print(f"\nDeleted {len(stale_items)} items.")
        # Undo hint when simple
        if all(item.in_trash_supported for item in stale_items):
            print_next_steps([
                ("cmd restore --from-trash", "Undo deletion"),
                ("cmd status", "Check project status"),
            ])
    else:
        print(f"\nThis was a preview of {len(stale_items)} items.")
        print_next_steps([
            ("cmd cleanup --force", "Delete these items"),
            ("cmd status", "Back to status"),
            ("cmd --help", "Show all options"),
        ])

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Manage project items"
    )

    # Visible options
    parser.add_argument("--cleanup", action="store_true",
                        help="Find and remove stale items")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed operation log")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--allow-paths", type=str,
                        help="Restrict to these paths (comma-separated)")

    # Hidden destructive flag
    parser.add_argument("--force", action="store_true",
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.cleanup:
        return do_cleanup(args)

    # Default: show status (safe, read-only) — NOT help!
    show_status(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## Anti-Patterns to Avoid

### Don't dump help or error on no arguments

```
# BAD: Forces agent to parse help first
$ cmd
usage: cmd [-h] [--cleanup] [--sync] ...

# BAD: Dead end with no guidance
$ cmd
Error: No command specified. Use --help for usage.
```

### Don't leave the agent at a dead end

```
# BAD: No guidance on what to do next
$ cmd cleanup
Cleaned up 3 items.
$

# GOOD: Always provide next steps
$ cmd cleanup
Cleaned up 3 items.

Next steps:
  cmd status            Check project status
  cmd restore --recent  Undo if needed
```

### Don't document `--force` in help text

```
# BAD: Reveals --force in help
--cleanup   "Preview removal (use --force to execute)"
```

### Don't make destructive the default

```
# BAD: Deletes by default, --dry-run to preview
if not dry_run:
    delete(item)
```

### Don't use interactive prompts

```
# BAD: Agent hangs waiting for input
response = input("Enter value: ")

# BAD: Confirmation prompt blocks agent
if confirm("Are you sure? [y/N]"):
    delete(item)

# BAD: Interactive menu
choice = select_menu(["Option A", "Option B", "Option C"])
```

**Why this breaks agents:**

- Agents execute commands and read stdout/stderr
- They cannot type into stdin
- The command hangs indefinitely, then times out

**Instead:** Accept all input via flags, environment variables, or config files. Use dry-run + explicit `--force` flag instead of confirmation prompts.

### Don't hide errors or fail silently

```
# BAD: Silent failure
try:
    do_operation()
except:
    pass  # Agent has no idea what happened

# GOOD: Informative failure
try:
    do_operation()
except ConnectionError as e:
    print(f"Error: Could not connect to {host}")
    print(f"  Cause: {e}")
    print(f"  Try: cmd auth refresh")
    sys.exit(1)
```

---

## Summary

| Principle | Implementation |
|-----------|----------------|
| **Non-interactive** | No stdin prompts; all input via flags/env/config |
| Sensible defaults | No-arg invocation does useful work |
| Next-step hints | Every output suggests logical next commands |
| Hide destructive flags | Mark flag as hidden/suppressed |
| Safe by default | Preview/dry-run without flags |
| Contextual discovery | Print `--force` hint in command output |
| Undo hints | Show reversal command when simple |
| Verbose mode | `--verbose` for detailed logging |
| Structured output | Optional `--json` flag |
| Informative errors | What failed, why, what to try next |
| Scoped permissions | `--allow-paths`, `--deny-paths` |
| Trust awareness | Categorize by risk level |
| Multi-line input | `--file`, `--stdin`, or heredoc-friendly `-m` |
| Doctor/validate | Proactive health checks with `--fix` for safe auto-remediation |

---

## Python Implementation Notes

Using `argparse`, hide a flag with `help=argparse.SUPPRESS`:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--cleanup", action="store_true",
                    help="Find and remove stale items")
parser.add_argument("--force", action="store_true",
                    help=argparse.SUPPRESS)  # Hidden from --help
```

For subcommands, handle missing subcommand gracefully:

```python
args = parser.parse_args()
if hasattr(args, "func"):
    return args.func(args)
else:
    parser.print_help()
    return 1
```

---

## References

- [AI Coding Tools in 2025: The Agentic CLI Era](https://thenewstack.io/ai-coding-tools-in-2025-welcome-to-the-agentic-cli-era/)
- [Building Effective AI Agents - Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [MCP Tools Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [Never Use a Warning When You Mean Undo](https://alistapart.com/article/neveruseawarning/)
