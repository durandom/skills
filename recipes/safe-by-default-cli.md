# Recipe: Safe-by-Default CLI for AI Agents

**Target Audience:** AI Coding Agents (Claude, Gemini, Copilot)
**Goal:** Design CLI tools where destructive operations require explicit discovery, preventing AI agents from skipping safety steps.

## The Philosophy: "Capability Gradient"

AI agents parse `--help` to understand available options. If destructive flags are visible, agents may use them immediately without understanding the consequences.

**Solution:** Create a two-step workflow where:

1. **Safe operations** are advertised in `--help`
2. **Destructive operations** are hidden and only revealed in command output

This forces agents (and humans) to run the safe version first, see what would happen, then explicitly opt into the destructive action.

## The Pattern

### Level 1: Hide Destructive Flags from Help

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

### Level 2: Dry-Run by Default

Make the safe behavior the default. When `--cleanup` runs without `--force`:

```
function do_cleanup(items, execute):
    if items is empty:
        print "✓ Nothing to clean up."
        return

    for each item in items:
        if execute:
            delete(item)
            print "  ✓ deleted: {item}"
        else:
            print "  would delete: {item}"

    if not execute:
        # Discovery path: reveal --force HERE
        print "This was a preview. Run with --force to delete."
```

### Level 3: Discovery Through Output

The key insight: **reveal capabilities contextually**. Different commands guide to different uses of `--force`:

```
# In check mode - guides to fixing drift
if drift_found:
    print "Run `cmd --force` to fix drift."

# In cleanup mode - guides to actual deletion
if stale_found:
    print "Run `cmd --cleanup --force` to remove them."
```

## Complete Example

```
command setup:
    options:
        --cleanup   "Find and remove stale items"   # Visible
        --force     HIDDEN                          # Invisible

    if cleanup flag set:
        stale_items = storage.get_stale_items()

        if stale_items is empty:
            print "✓ No stale items."
            return

        for each item in stale_items:
            if force flag set:
                storage.delete(item)
                print "  ✓ deleted: {item}"
            else:
                print "  would delete: {item}"

        if force flag not set:
            print "This was a preview. Run with --force to delete."
        return

    # Default: safe setup
    storage.setup()
```

## Why This Works for AI Agents

| Agent Behavior | Without This Pattern | With This Pattern |
|----------------|---------------------|-------------------|
| Parses `--help` | Sees `--force`, uses it immediately | Only sees safe options |
| Runs command | May delete without preview | Gets preview first |
| Sees output | - | Learns about `--force` contextually |
| Second attempt | - | Now can use `--force` intentionally |

## Anti-Patterns to Avoid

❌ **Don't:** Document `--force` in the help text of other flags

```
# BAD: Reveals --force in help
--cleanup   "Preview removal (use --force to execute)"
```

❌ **Don't:** Make destructive the default

```
# BAD: Deletes by default, --dry-run to preview
if not dry_run:
    delete(item)
```

✅ **Do:** Safe by default, hidden escape hatch

```
# GOOD: Preview by default, --force hidden
if force:
    delete(item)
else:
    print "would delete: {item}"
```

## Summary

| Principle | Implementation |
|-----------|----------------|
| Hide destructive flags | Mark flag as hidden/suppressed |
| Safe by default | Preview/dry-run without flags |
| Contextual discovery | Print `--force` hint in command output |
| Explicit opt-in | Require running safe version first |

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
