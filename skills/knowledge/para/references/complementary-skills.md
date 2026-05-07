# Complementary Skills: GTD

## What is GTD?

GTD (Getting Things Done) is David Allen's methodology for personal productivity. It provides a trusted workflow for capturing, clarifying, organizing, and reviewing commitments — turning "stuff" into actionable next steps.

## How GTD Complements PARA

PARA is a **filing cabinet** — it organizes your notes and documents. GTD is a **workflow engine** — it tracks what to do next. Together they cover both organization and execution, but neither requires the other.

| System | Handles | Typical Storage |
|--------|---------|-----------------|
| PARA | Notes, documentation, reference files | Filesystem folders |
| GTD | Task tracking, next actions, reviews | gtd CLI |

## Optional Sync Points

If you use both skills, you may find these natural alignment points useful:

- **Projects:** A PARA project folder often has a matching GTD project tracking its tasks and next actions
- **Areas:** PARA's `2_Areas/` maps to GTD's H2 "Areas of Focus" — both represent ongoing responsibilities
- **Archive:** Archiving a PARA folder is a natural time to close the corresponding GTD project

These are conventions, not enforced rules. Each skill works independently.

## Manual Alignment Check

During a PARA review, you can optionally compare your project lists:

1. List your PARA project folders (`ls 1_Projects/`)
2. List your GTD projects (`gtd project list`)
3. Look for mismatches:
   - **PARA-only** — is this still active? Consider archiving, or creating a GTD project
   - **GTD-only** — consider creating a PARA folder for working documents
   - **Name drift** — keep names consistent across both systems

This is a lightweight manual check, not an automated sync. Do it when it feels useful, skip it when it doesn't.

## PARA Reference Index

- [para-method.md](../references/para-method.md) - Full PARA methodology with examples
- [decision-tree.md](../references/decision-tree.md) - PARA categorization decision tree
- [common-mistakes.md](../references/common-mistakes.md) - PARA anti-patterns and fixes
