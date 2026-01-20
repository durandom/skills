# Compact Output Spec

Delta spec for compact CLI output formatting.

## ADDED Requirements

### Requirement: Compact check summary on success

The CLI SHALL display a compact summary line when all health checks pass, instead of listing each check individually.

Format: `✓ N/N checks passed`

#### Scenario: All checks pass

- **WHEN** `layton` is invoked with no args AND all doctor checks pass
- **THEN** output includes `✓ 4/4 checks passed` (or equivalent count)
- **AND** individual check details are NOT included in output

#### Scenario: All checks pass with verbose flag

- **WHEN** `layton --verbose` is invoked AND all checks pass
- **THEN** output includes full check details for each check
- **AND** each check shows name, status, and message

### Requirement: Expanded output on failure

The CLI SHALL display full check details when any health check fails, to aid debugging.

#### Scenario: One check fails

- **WHEN** `layton` is invoked AND one or more checks fail
- **THEN** output includes details for ALL checks (pass and fail)
- **AND** failed checks show diagnostic information

#### Scenario: Config missing shows full output

- **WHEN** `layton` is invoked AND config_exists check fails
- **THEN** output shows all check results with details
- **AND** the config_exists failure includes the expected config path

### Requirement: JSON output unchanged

The CLI SHALL maintain current JSON structure for machine parsing. Compact formatting applies only to human-readable output.

#### Scenario: JSON output with all checks passing

- **WHEN** `layton` is invoked (default JSON mode) AND all checks pass
- **THEN** output is valid JSON with full `checks` array
- **AND** each check object includes `name`, `status`, `message`

#### Scenario: Human flag shows compact

- **WHEN** `layton --human` is invoked AND all checks pass
- **THEN** output shows compact summary (not JSON)
- **AND** summary line shows check count

## Test Mapping

| Scenario | Test File | Test Function |
|----------|-----------|---------------|
| All checks pass | `tests/layton/e2e/test_orientation_e2e.py` | `test_compact_summary_on_success` |
| Verbose flag | `tests/layton/e2e/test_orientation_e2e.py` | `test_verbose_shows_all_checks` |
| One check fails | `tests/layton/e2e/test_orientation_e2e.py` | `test_expanded_output_on_failure` |
| JSON unchanged | `tests/layton/e2e/test_orientation_e2e.py` | `test_json_output_unchanged` |
| Human compact | `tests/layton/e2e/test_orientation_e2e.py` | `test_orientation_human_output` (existing) |
