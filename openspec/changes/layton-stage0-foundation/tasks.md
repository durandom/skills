## 1. Project Setup

- [ ] 1.1 Create `skills/layton/` directory structure with `laytonlib/` flat package
- [ ] 1.2 Create `skills/layton/scripts/layton` CLI entrypoint (thin wrapper)
- [ ] 1.3 Create `laytonlib/__init__.py` and `laytonlib/__main__.py`
- [ ] 1.4 Create test directory structure `tests/layton/` with `conftest.py` fixtures

## 2. CLI Framework (cli-framework spec)

- [ ] 2.1 Create `laytonlib/cli.py` with argparse structure and global options (`--human`, `--verbose`, `--help`, `--version`)
- [ ] 2.2 Create `laytonlib/formatters.py` with `OutputFormatter` (JSON default, human-readable with `--human`)
- [ ] 2.3 Implement consistent JSON response structure (`success`, `data`, `error`, `next_steps`)
- [ ] 2.4 Implement exit codes (0=success, 1=fixable, 2=critical)
- [ ] 2.5 Implement no-arg default (`layton` → `layton doctor`, `layton config` → `layton config show`)

## 3. Doctor Command (cli-doctor spec)

- [ ] 3.1 Create `laytonlib/doctor.py` with health check logic
- [ ] 3.2 Implement `beads_available` check (verify `bd` in PATH and `bd info --json` succeeds)
- [ ] 3.3 Implement `beads_initialized` check (warn if `.beads/` missing)
- [ ] 3.4 Implement `config_exists` check (fail if `.layton/config.json` missing)
- [ ] 3.5 Implement `config_valid` check (fail if invalid JSON)
- [ ] 3.6 Implement hidden `--fix` flag (creates config with defaults)
- [ ] 3.7 Add `next_steps` suggestions based on check results
- [ ] 3.8 Write unit tests for doctor checks (mock `bd` availability)
- [ ] 3.9 Write e2e tests for `layton doctor` command

## 4. Config Commands (cli-config spec)

- [ ] 4.1 Create `laytonlib/config.py` with config file loading/saving logic
- [ ] 4.2 Implement git root detection for config path (`<git-root>/.layton/config.json`)
- [ ] 4.3 Implement `layton config init` (create config with defaults, error if exists)
- [ ] 4.4 Implement `layton config init --force` (overwrite existing)
- [ ] 4.5 Implement `layton config show` (dump entire config as JSON)
- [ ] 4.6 Implement `layton config keys` (list all dot-notation paths)
- [ ] 4.7 Implement `layton config get <key>` with dot-notation traversal
- [ ] 4.8 Implement `layton config set <key> <value>` (update/create nested paths, parse JSON values)
- [ ] 4.9 Write unit tests for config loading/saving
- [ ] 4.10 Write e2e tests for all config subcommands

## 5. Context Command (cli-context spec)

- [ ] 5.1 Create `laytonlib/context.py` with temporal context logic
- [ ] 5.2 Implement time-of-day classification (morning/midday/afternoon/evening/night)
- [ ] 5.3 Implement work hours calculation from config
- [ ] 5.4 Implement timezone handling from config
- [ ] 5.5 Implement JSON output (timestamp, time_of_day, day_of_week, work_hours, timezone)
- [ ] 5.6 Implement human-readable output with natural language summary
- [ ] 5.7 Implement error handling for missing config (CONFIG_MISSING)
- [ ] 5.8 Write unit tests for temporal classification
- [ ] 5.9 Write e2e tests for `layton context` command

## 6. SKILL.md and Workflows (beads-conventions spec)

- [ ] 6.1 Create `skills/layton/SKILL.md` router with XML structure
- [ ] 6.2 Create `skills/layton/workflows/morning-briefing.md`
- [ ] 6.3 Create `skills/layton/workflows/track-item.md`
- [ ] 6.4 Create `skills/layton/workflows/set-focus.md`
- [ ] 6.5 Create `skills/layton/references/beads-commands.md`
- [ ] 6.6 Create `skills/layton/references/persona.md` (placeholder for Stage 1)

## 7. Integration & Documentation

- [ ] 7.1 Run full test suite and ensure all tests pass
- [ ] 7.2 Test CLI manually in isolated environment
- [ ] 7.3 Verify Beads integration with real `bd` CLI
