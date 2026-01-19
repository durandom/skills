## 1. Project Setup

- [x] 1.1 Create `skills/layton/` directory structure with `laytonlib/` flat package
- [x] 1.2 Create `skills/layton/scripts/layton` CLI entrypoint (thin wrapper)
- [x] 1.3 Create `laytonlib/__init__.py` and `laytonlib/__main__.py`
- [x] 1.4 Create test directory structure `tests/layton/` with `conftest.py` fixtures

## 2. CLI Framework (cli-framework spec)

- [x] 2.1 Create `laytonlib/cli.py` with argparse structure and global options (`--human`, `--verbose`, `--help`, `--version`)
- [x] 2.2 Create `laytonlib/formatters.py` with `OutputFormatter` (JSON default, human-readable with `--human`)
- [x] 2.3 Implement consistent JSON response structure (`success`, `data`, `error`, `next_steps`)
- [x] 2.4 Implement exit codes (0=success, 1=fixable, 2=critical)
- [x] 2.5 Implement no-arg default (`layton` → `layton doctor`, `layton config` → `layton config show`)

## 3. Doctor Command (cli-doctor spec)

- [x] 3.1 Create `laytonlib/doctor.py` with health check logic
- [x] 3.2 Implement `beads_available` check (verify `bd` in PATH and `bd info --json` succeeds)
- [x] 3.3 Implement `beads_initialized` check (warn if `.beads/` missing)
- [x] 3.4 Implement `config_exists` check (fail if `.layton/config.json` missing)
- [x] 3.5 Implement `config_valid` check (fail if invalid JSON)
- [x] 3.6 Implement hidden `--fix` flag (creates config with defaults)
- [x] 3.7 Add `next_steps` suggestions based on check results
- [x] 3.8 Write unit tests for doctor checks (mock `bd` availability)
- [x] 3.9 Write e2e tests for `layton doctor` command

## 4. Config Commands (cli-config spec)

- [x] 4.1 Create `laytonlib/config.py` with config file loading/saving logic
- [x] 4.2 Implement git root detection for config path (`<git-root>/.layton/config.json`)
- [x] 4.3 Implement `layton config init` (create config with defaults, error if exists)
- [x] 4.4 Implement `layton config init --force` (overwrite existing)
- [x] 4.5 Implement `layton config show` (dump entire config as JSON)
- [x] 4.6 Implement `layton config keys` (list all dot-notation paths)
- [x] 4.7 Implement `layton config get <key>` with dot-notation traversal
- [x] 4.8 Implement `layton config set <key> <value>` (update/create nested paths, parse JSON values)
- [x] 4.9 Write unit tests for config loading/saving
- [x] 4.10 Write e2e tests for all config subcommands

## 5. Context Command (cli-context spec)

- [x] 5.1 Create `laytonlib/context.py` with temporal context logic
- [x] 5.2 Implement time-of-day classification (morning/midday/afternoon/evening/night)
- [x] 5.3 Implement work hours calculation from config
- [x] 5.4 Implement timezone handling from config
- [x] 5.5 Implement JSON output (timestamp, time_of_day, day_of_week, work_hours, timezone)
- [x] 5.6 Implement human-readable output with natural language summary
- [x] 5.7 Implement error handling for missing config (CONFIG_MISSING)
- [x] 5.8 Write unit tests for temporal classification
- [x] 5.9 Write e2e tests for `layton context` command

## 6. SKILL.md and Workflows (beads-conventions spec)

- [x] 6.1 Create `skills/layton/SKILL.md` router with XML structure
- [x] 6.2 Create `skills/layton/workflows/morning-briefing.md`
- [x] 6.3 Create `skills/layton/workflows/track-item.md`
- [x] 6.4 Create `skills/layton/workflows/set-focus.md`
- [x] 6.5 Create `skills/layton/references/beads-commands.md`
- [x] 6.6 Create `skills/layton/references/persona.md` (placeholder for Stage 1)

## 7. Integration & Documentation

- [x] 7.1 Run full test suite and ensure all tests pass
- [x] 7.2 Test CLI manually in isolated environment
- [x] 7.3 Verify Beads integration with real `bd` CLI
