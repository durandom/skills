# Recipe: Beads + Dolt Server Setup (macOS)

Repeatable setup for [beads](https://github.com/steveyegge/beads) (`bd`) with a Dolt SQL server on macOS. Covers install, per-project initialization, JSONL migration, and maintenance.

**Tested:** 2026-02-27 — bd v0.56.1, dolt v1.82.6

## Overview

Since beads v0.56.0, embedded mode was removed (binary shrank from 168 MB to 41 MB). A running Dolt SQL server is now required. One server hosts multiple project databases.

```
┌─────────────────────────────────────────┐
│         Dolt SQL Server (:3307)         │
│                                         │
│  ┌──────────┐ ┌──────┐ ┌────────────┐  │
│  │ project-a│ │proj-b│ │ project-c  │  │
│  │ (database)│ │(db)  │ │ (database) │  │
│  └──────────┘ └──────┘ └────────────┘  │
└─────────────────────────────────────────┘
```

## 1. Install

```bash
brew install beads
# or: go install github.com/steveyegge/beads/cmd/bd@latest

brew install dolt
```

## 2. Configure Dolt Server

Beads defaults to port 3307 (avoids MySQL conflict on 3306).

The Homebrew formula places config at `/opt/homebrew/etc/dolt/config.yaml` (created on first install). Change the port:

```yaml
# /opt/homebrew/etc/dolt/config.yaml
listener:
  host: localhost
  port: 3307
```

### Custom LaunchAgent (required until PR merges)

The current Homebrew formula's `service` block starts dolt **without** a `--config` flag, so it ignores `config.yaml` and falls back to port 3306. Additionally, `brew services` regenerates the plist on every `start`/`restart`, overwriting any manual edits.

> **Upstream fix pending:** [homebrew-core#269724](https://github.com/Homebrew/homebrew-core/pull/269724) — adds `--config` to the formula's service block. Once merged and installed via `brew upgrade dolt`, delete `local.dolt.plist` and use `brew services start dolt` instead.

The fix: use a **custom LaunchAgent with a different label** (`local.dolt`). Brew never touches plists it doesn't own.

```bash
# Stop and remove the brew-managed service
brew services stop dolt
```

Create `~/Library/LaunchAgents/local.dolt.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>local.dolt</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/bin/dolt</string>
    <string>sql-server</string>
    <string>--config</string>
    <string>/opt/homebrew/etc/dolt/config.yaml</string>
  </array>
  <key>WorkingDirectory</key><string>/opt/homebrew/var/dolt</string>
  <key>KeepAlive</key><true/>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>/opt/homebrew/var/log/dolt.log</string>
  <key>StandardErrorPath</key><string>/opt/homebrew/var/log/dolt.error.log</string>
</dict>
</plist>
```

Load and verify:

```bash
launchctl load -w ~/Library/LaunchAgents/local.dolt.plist

# Verify — "opsession-prxy" is the service name for port 3307
tail -1 /opt/homebrew/var/log/dolt.log
# Expected: HP="localhost:3307"

tail -1 /opt/homebrew/var/log/dolt.error.log
# Expected: "Server ready. Accepting connections."
```

## 3. Initialize Beads in a Project

```bash
cd ~/src/my-project

# Initialize (creates DB as "beads_<prefix>" automatically)
bd init --prefix my-project

# Verify connection
bd dolt test
bd dolt show    # Check the database name

# Claude Code integration
bd setup claude --project

# Git hooks
bd hooks install

# Claude plugin (project-scoped)
claude plugin install --scope project beads@beads-marketplace
```

## 4. Migrate Existing JSONL Data (pre-v0.56)

If a project has data in `issues.jsonl` from an older beads version:

```bash
# Backup first
cp .beads/issues.jsonl .beads/issues.jsonl.backup

# Create schema (--from-jsonl creates schema but does NOT import data)
bd init --from-jsonl --force --prefix my-project

# Import via Python script → produces SQL
python3 import_beads_jsonl.py <database-name> .beads/issues.jsonl > /tmp/import.sql
cd /opt/homebrew/var/dolt && dolt sql < /tmp/import.sql

# Verify
bd list --all
bd ready
```

### import_beads_jsonl.py

```python
#!/usr/bin/env python3
"""Import beads issues.jsonl into a Dolt database.

Usage: python3 import_beads_jsonl.py <database-name> [jsonl-path]
Outputs SQL to stdout. Pipe into dolt sql.
"""
import json, sys

DB = sys.argv[1]
JSONL = sys.argv[2] if len(sys.argv) > 2 else ".beads/issues.jsonl"

with open(JSONL) as f:
    issues = [json.loads(l) for l in f if l.strip()]

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

sql = [f"USE `{DB}`;"]
for i in issues:
    ca = esc(i.get("closed_at"))
    if ca == "''": ca = "NULL"
    sql.append(
        f"INSERT INTO issues (id, title, description, design, "
        f"acceptance_criteria, notes, status, priority, issue_type, "
        f"owner, created_at, created_by, updated_at, closed_at, "
        f"close_reason) VALUES ({esc(i['id'])}, {esc(i['title'])}, "
        f"{esc(i.get('description',''))}, '', '', "
        f"{esc(i.get('notes',''))}, {esc(i['status'])}, "
        f"{i.get('priority',2)}, {esc(i.get('issue_type','task'))}, "
        f"{esc(i.get('owner',''))}, {esc(i['created_at'])}, "
        f"{esc(i.get('created_by',''))}, {esc(i['updated_at'])}, "
        f"{ca}, {esc(i.get('close_reason',''))});")
    for d in i.get("dependencies", []):
        sql.append(
            f"INSERT INTO dependencies (issue_id, depends_on_id, type, "
            f"created_at, created_by) VALUES ({esc(d['issue_id'])}, "
            f"{esc(d['depends_on_id'])}, {esc(d['type'])}, "
            f"{esc(d['created_at'])}, {esc(d.get('created_by',''))});")

print("\n".join(sql))
```

## 5. Maintenance

| Task | Command |
|------|---------|
| Server status | `launchctl list \| grep dolt` |
| Test connection | `bd dolt test` |
| Logs | `tail /opt/homebrew/var/log/dolt.error.log` |
| List databases | `ls /opt/homebrew/var/dolt/` |
| Diagnostics | `bd doctor` |
| Restart server | `launchctl unload ~/Library/LaunchAgents/local.dolt.plist && launchctl load -w ~/Library/LaunchAgents/local.dolt.plist` |

## Gotchas

| Trap | Why | Do Instead |
|------|-----|------------|
| Using label `homebrew.mxcl.dolt` in your plist | `brew services` regenerates and overwrites it | Use label `local.dolt` in a separate `local.dolt.plist` |
| Homebrew formula starts dolt without `--config` | Service block has no `--config` flag → falls back to port 3306 | Use the custom `local.dolt.plist` with explicit `--config` |
| `brew services restart dolt` | Regenerates the plist, loses `--config` flag | Ignore `brew services` for dolt; use `launchctl unload`/`load` on `local.dolt.plist` |
| `brew upgrade dolt` | Does not reload the LaunchAgent | `launchctl unload` / `load ~/Library/LaunchAgents/local.dolt.plist` after upgrade |
| Orphan dolt processes on random ports | `bd` auto-starts per-project servers when it can't reach port 3307 | Before `bd init`, run `bd dolt killall` to clear orphans |
| `.beads/dolt-server.port` has stale port | Created when `bd` auto-starts a per-project server; ignored once file is gone | `rm .beads/dolt-server.port` — beads will auto-detect 3307 on next run |
| `bd init` says "workspace already initialized" with wrong port | Database exists on 3307 from a previous failed init; beads uses cached port | `bd init --force --server-port 3307 --prefix <name>` |
| `.beads/dolt/config.yaml` has wrong port | `bd init` stores the port of the first server it connects to — even an orphan | After `bd init`, verify `listener.port` in `.beads/dolt/config.yaml` is 3307; fix with `sed -i '' 's/port: .*/port: 3307/' .beads/dolt/config.yaml` |
| Running `bd dolt set database` after `bd init` | Creates a second empty DB, breaks schema link | Let `bd init --prefix` handle it |
| `bd init --from-jsonl` | Creates schema only, does NOT import data | Use the Python import script above |
| Looking for Dolt data in `~` | Data lives in `/opt/homebrew/var/dolt` | Always `cd` there for direct `dolt sql` |
| Wrong init order | `bd init` must run before any `bd dolt set` | Just use `bd init --prefix` end-to-end |
