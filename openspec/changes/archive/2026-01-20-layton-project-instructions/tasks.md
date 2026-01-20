# Implementation Tasks

## 1. Project Instructions Documentation

- [x] 1.1 Create `references/project-instructions.md` with best practices
- [x] 1.2 Document CLAUDE.md purpose (human-readable context, entry points, structure)
- [x] 1.3 Document AGENTS.md purpose (mechanical rules, quick refs, session protocol)
- [x] 1.4 Add anti-patterns section (verbosity, duplication, missing sections)
- [x] 1.5 Create `examples/CLAUDE.md` (genericized from pensieve-rhdh pattern)
- [x] 1.6 Create `examples/AGENTS.md` (concise, under 50 lines)

## 2. Tests for Project Instructions

- [x] 2.1 Create `tests/layton/unit/test_project_instructions.py`
- [x] 2.2 Add `test_reference_doc_exists`
- [x] 2.3 Add `test_reference_covers_claude_md`
- [x] 2.4 Add `test_reference_covers_agents_md`
- [x] 2.5 Add `test_reference_includes_antipatterns`
- [x] 2.6 Add `test_example_claude_md_exists`
- [x] 2.7 Add `test_example_claude_md_sections`
- [x] 2.8 Add `test_example_agents_md_exists`
- [x] 2.9 Add `test_example_agents_md_sections`

## 3. Audit Workflow

- [x] 3.1 Create `workflows/audit-project-instructions.md`
- [x] 3.2 Add YAML frontmatter (name, description, triggers)
- [x] 3.3 Document step: Read target CLAUDE.md and AGENTS.md
- [x] 3.4 Document step: Check for missing files
- [x] 3.5 Document step: Analyze verbosity and duplication
- [x] 3.6 Document step: Check for missing recommended sections
- [x] 3.7 Document step: Present findings as suggestions (not auto-apply)

## 4. Tests for Audit Workflow

- [x] 4.1 Add `test_audit_workflow_exists` to `tests/layton/unit/test_workflows.py`
- [x] 4.2 Add `test_audit_workflow_triggers`

## 5. Retrospect Workflow

- [x] 5.1 Create `workflows/retrospect.md`
- [x] 5.2 Add YAML frontmatter (name, description, triggers)
- [x] 5.3 Document step: Identify completed workflow
- [x] 5.4 Document step: Evaluate goal achievement
- [x] 5.5 Document step: Identify friction points
- [x] 5.6 Document step: Suggest improvements
- [x] 5.7 Document step: Offer to capture changes (user confirms)

## 6. Tests for Retrospect Workflow

- [x] 6.1 Add `test_retrospect_workflow_exists` to `tests/layton/unit/test_workflows.py`
- [x] 6.2 Add `test_retrospect_workflow_triggers`

## 7. Setup Workflow Modification

- [x] 7.1 Update `workflows/setup.md` to mention audit workflow in "Suggest Workflows" step
- [x] 7.2 Make audit mention optional ("Would you like to...")
- [x] 7.3 Add `test_setup_mentions_audit_workflow` to tests

## 8. Compact CLI Output

- [x] 8.1 Modify `laytonlib/` to format check summary as `✓ N/N checks passed` on success
- [x] 8.2 Expand to full output when any check fails
- [x] 8.3 Add `--verbose` flag to force full output
- [x] 8.4 Ensure JSON output unchanged (compact only affects human output)

## 9. Tests for Compact Output

- [x] 9.1 Add `test_compact_summary_on_success` to `tests/layton/e2e/test_orientation_e2e.py`
- [x] 9.2 Add `test_verbose_shows_all_checks`
- [x] 9.3 Add `test_expanded_output_on_failure`
- [x] 9.4 Add `test_json_output_unchanged`

## 10. Verification

- [x] 10.1 Run full test suite: `uv run pytest tests/layton/`
- [ ] 10.2 Manual test: Run audit workflow on a sample repo
- [ ] 10.3 Manual test: Run retrospect workflow after another workflow
- [x] 10.4 Verify compact output with all checks passing
