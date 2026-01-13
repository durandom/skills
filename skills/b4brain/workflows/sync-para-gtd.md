# Workflow: Sync PARA Projects with GTD Milestones

Ensure PARA project folders stay in sync with GTD project milestones.

<objective>
Compare PARA project folders with GTD milestones and identify/fix mismatches.
</objective>

<process>

## Step 1: Get Current State

Run both commands to see the current state:

```bash
# List PARA project folders
./.claude/skills/para/scripts/para project list

# List GTD projects (milestones)
./.claude/skills/gtd/scripts/gtd project list --state open
```

## Step 2: Identify Mismatches

Compare the two lists:

- **Synced:** Items present in both PARA and GTD
- **PARA-only:** Folders in `1 Projects/` with no matching GTD milestone
- **GTD-only:** GTD milestones with no matching PARA folder

## Step 3: Present Findings

Format the comparison for the user:

```
## Sync Status

**Synced:** [count]
- Project-A
- Project-B

**PARA-only (no GTD milestone):** [count]
- Old-Project (consider: archive or create GTD milestone?)

**GTD-only (no PARA folder):** [count]
- New-Project (consider: create PARA folder?)
```

## Step 4: Ask User What to Fix

Use `AskUserQuestion` to present options:

For **PARA-only** items:

1. Create GTD milestone
2. Archive PARA folder (project completed)
3. Leave as-is

For **GTD-only** items:

1. Create PARA folder
2. Close GTD milestone (if no longer relevant)
3. Leave as-is

## Step 5: Execute Chosen Fixes

Based on user choices:

**Creating PARA folder:**

```bash
./.claude/skills/para/scripts/para project create "Project-Name"
```

**Creating GTD milestone:**

```bash
./.claude/skills/gtd/scripts/gtd project create "Project-Name"
```

**Archiving PARA folder:**

```bash
./.claude/skills/para/scripts/para project archive "Project-Name"
```

**Closing GTD milestone:**

```bash
./.claude/skills/gtd/scripts/gtd project update "Project-Name" --state closed
```

</process>

<naming_convention>

## Project Naming

Project names should:

- Use kebab-case or PascalCase (be consistent)
- Match **exactly** between PARA and GTD
- Be descriptive but concise

**Examples:**

- `API-Redesign-v2`
- `Q4-Security-Audit`
- `Team-Onboarding-2024`

</naming_convention>

<success_criteria>

- All PARA projects have corresponding GTD milestones (or user explicitly chose to leave as-is)
- All GTD milestones have corresponding PARA folders (or user explicitly chose to leave as-is)
- User understands any remaining mismatches and why they exist
</success_criteria>
