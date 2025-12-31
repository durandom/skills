# Plan: Test Python Repo for code-map Skill

## Goal
Add a test Python repository at project root that:
1. Acts as a realistic template to test the code-map skill
2. Uses snapshot testing (syrupy) per `recipes/snapshot-testing.md`
3. Keeps skill directory clean for distribution

## Current State
- Existing: `skills/code-map/scripts/tests/` with fixtures inside skill
- No `pyproject.toml` at project root
- No syrupy/snapshot tests configured

## Proposed Structure

```
durandom/                          # Project root
├── pyproject.toml                 # NEW: Project config + dev deps
├── tests/                         # NEW: All tests at root
│   ├── conftest.py               # syrupy fixture
│   ├── code_map/                 # Tests for code-map skill
│   │   ├── test_validate_map.py  # MOVED from skill
│   │   ├── test_lsp_client.py    # MOVED from skill
│   │   └── test_validate_map_snapshot.py  # NEW: snapshot tests
│   └── __snapshots__/            # syrupy output
├── fixtures/                      # NEW: Test fixtures at root
│   └── calculator/               # Realistic Python project
│       ├── src/calculator/
│       │   ├── __init__.py
│       │   ├── core.py           # Calculator class
│       │   └── operations.py     # add, subtract, etc.
│       └── docs/map/             # Code map for this project
│           ├── MAP.md
│           ├── ARCHITECTURE.md
│           └── domains/calculator.md
├── skills/
│   └── code-map/                 # CLEAN: no tests/fixtures
│       ├── SKILL.md
│       ├── scripts/              # Only production scripts
│       │   ├── validate_map.py
│       │   └── lsp_client.py
│       ├── workflows/
│       ├── templates/
│       └── references/
└── ...
```

## Implementation Steps

1. Create `pyproject.toml` at project root
2. Create `fixtures/calculator/` with Python package + code map
3. Create `tests/conftest.py` with syrupy fixture
4. Move existing tests from `skills/code-map/scripts/tests/` to `tests/code_map/`
5. Add `tests/code_map/test_validate_map_snapshot.py` with Printer-pattern tests
6. Remove `skills/code-map/scripts/tests/` directory
7. Run tests and approve initial snapshots
