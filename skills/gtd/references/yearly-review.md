# Yearly Review Workflow

**Cadence:** Once per year (end of year or start of new year)
**Duration:** ~2 hours

## Purpose

Review your vision and purpose, assess yearly goal completion, celebrate accomplishments, and set intentions for the coming year.

## Horizon Tracking Reference

| Horizon | Where | During Yearly Review |
|---------|-------|---------------------|
| H3 (Goals) | GTD items (`horizon/goal`) | Review, close completed, create new |
| H2 (Areas) | `2_Areas/` folder in vault | Check balance, add/retire areas |
| H4 (Vision) | `HORIZONS.md` at vault root | Reflect, update if needed |
| H5 (Purpose) | `HORIZONS.md` at vault root | Reflect, update if needed |

**Key distinction:**

- H3 goals are **trackable GTD items** — you close them when achieved
- H4/H5 are **prose in HORIZONS.md** — you reflect and update, not "complete"

## Steps

### 1. Review Goals Completion (H3)

List all goals tracked as issues:

```bash
$GTD list --horizon goal --state all
```

For completed goals: Celebrate! Then close if not already closed.
For open goals: Still relevant? Need adjustment? Should be closed?

**Note:** If this shows nothing, you haven't been tracking goals as GTD items. Consider adding key goals for the coming year.

### 2. Review Projects Completed (H1)

Acknowledge your project completions:

```bash
$GTD projects --state closed
```

Count and celebrate these wins!

### 3. Review Higher Horizons (H4/H5 — HORIZONS.md)

Open `HORIZONS.md` at your **vault root** (not the template in skills/gtd/references/).

**Purpose & Principles (H5):**

- What is my life's purpose?
- Am I living according to my principles?
- Are there new principles I want to adopt?

**Vision (H4):**

- Does my 3-5 year vision still inspire me?
- Am I on track toward this vision?
- Does my vision need updating?

### 4. Review Areas of Focus (H2 — Vault Folders)

Check your `2_Areas/` folder in the vault:

```bash
ls 2\ Areas/
```

- Are these still my key areas?
- Am I neglecting any area?
- Should I add or remove any?

### 5. Yearly Reflection Questions

Spend time journaling or thinking about:

- What were my biggest wins this year?
- What lessons did I learn?
- What am I most grateful for?
- What was my biggest challenge?
- What do I want to accomplish next year?
- Is my vision still inspiring?
- Are my areas of focus balanced?
- What should I let go of?

### 6. Set Up Next Year

**Archive completed goals:**

```bash
$GTD done <goal-id>
```

**Create new yearly goals:**

```bash
$GTD add "2027: [Your goal here]" --horizon goal
```

**Define initial projects to achieve those goals:**

```bash
$GTD add "Project to achieve goal" --horizon project
```

**Update HORIZONS.md** with any changes to H4 (Vision) or H5 (Purpose).

## Completion

Running `gtd yearly` automatically marks the yearly review as complete.

## Key Principle

The yearly review is about meaning and direction, not tasks. Step back from the tactical and ask: Is my life heading where I want it to go?

## First-Time Setup

If you don't have a `HORIZONS.md` yet, copy the template:

```bash
cp .claude/skills/gtd/references/horizons.md HORIZONS.md
```

Then fill in your H5 (Purpose & Principles) and H4 (Vision).
