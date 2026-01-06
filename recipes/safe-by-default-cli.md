# Recipe: Safe-by-Default CLI for AI Agents

**Target Audience:** AI Coding Agents (Claude, Gemini, Copilot)
**Goal:** Design CLI tools where destructive operations require explicit discovery, preventing AI agents from skipping safety steps.
**Tools:** `argparse` (Python), any CLI framework

## The Philosophy: "Capability Gradient"

AI agents parse `--help` to understand available options. If destructive flags are visible, agents may use them immediately without understanding the consequences.

**Solution:** Create a two-step workflow where:

1. **Safe operations** are advertised in `--help`
2. **Destructive operations** are hidden and only revealed in command output

This forces agents (and humans) to run the safe version first, see what would happen, then explicitly opt into the destructive action.

## The Pattern

### Level 1: Hide Destructive Flags from Help

Use `argparse.SUPPRESS` to make a flag functional but invisible in `--help`:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--cleanup",
    action="store_true",
    help="Find and remove stale items",  # Visible, sounds safe
)
parser.add_argument(
    "--force",
    action="store_true",
    help=argparse.SUPPRESS,  # Hidden from --help
)
```

**Result of `--help`:**

```
options:
  --cleanup   Find and remove stale items
```

No `--force` visible. An AI agent will naturally try `--cleanup` first.

### Level 2: Dry-Run by Default

Make the safe behavior the default. When `--cleanup` runs without `--force`:

```python
def do_cleanup(items, execute=False):
    if not items:
        print("✓ Nothing to clean up.")
        return 0

    print("Cleanup Preview" if not execute else "Executing Cleanup")
    print("=" * 40)

    for item in items:
        if execute:
            delete(item)
            print(f"  ✓ deleted: {item}")
        else:
            print(f"  would delete: {item}")

    if not execute:
        # Discovery path: tell them about --force HERE
        print("\nThis was a preview. Run with --force to delete.")

    return 0
```

### Level 3: Discovery Through Output

The key insight: **reveal capabilities contextually**. Different commands guide to different uses of `--force`:

```python
# In check mode - guides to fixing drift
if drift_found:
    print("Run `cmd --force` to fix drift.")

# In cleanup mode - guides to actual deletion
if stale_found:
    print("Run `cmd --cleanup --force` to remove them.")
```

## Complete Example

```python
import argparse

def cmd_setup(args):
    storage = get_storage()

    # Cleanup mode - preview by default
    if args.cleanup:
        stale = storage.get_stale_items()
        if not stale:
            print("✓ No stale items.")
            return 0

        for item in stale:
            if args.force:
                storage.delete(item)
                print(f"  ✓ deleted: {item}")
            else:
                print(f"  would delete: {item}")

        if not args.force:
            print("\nThis was a preview. Run with --force to delete.")
        return 0

    # Default: safe setup
    storage.setup()
    return 0

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()

    p = sub.add_parser("setup", help="Set up the system")
    p.add_argument("--cleanup", action="store_true",
                   help="Find and remove stale items")
    p.add_argument("--force", action="store_true",
                   help=argparse.SUPPRESS)  # Hidden!
    p.set_defaults(func=cmd_setup)

    args = parser.parse_args()
    return args.func(args)
```

## Why This Works for AI Agents

| Agent Behavior | Without This Pattern | With This Pattern |
|----------------|---------------------|-------------------|
| Parses `--help` | Sees `--force`, uses it immediately | Only sees safe options |
| Runs command | May delete without preview | Gets preview first |
| Sees output | - | Learns about `--force` contextually |
| Second attempt | - | Now can use `--force` intentionally |

## Anti-Patterns to Avoid

**Don't:** Document `--force` in the help text of other flags

```python
# BAD: Reveals --force in help
help="Preview removal (use --force to execute)"
```

**Don't:** Make destructive the default

```python
# BAD: Deletes by default, --dry-run to preview
if not args.dry_run:
    delete(item)
```

**Do:** Safe by default, hidden escape hatch

```python
# GOOD: Preview by default, --force hidden
if args.force:
    delete(item)
else:
    print(f"would delete: {item}")
```

## Summary

| Principle | Implementation |
|-----------|----------------|
| Hide destructive flags | `help=argparse.SUPPRESS` |
| Safe by default | Preview/dry-run without flags |
| Contextual discovery | Print `--force` hint in command output |
| Explicit opt-in | Require running safe version first |
