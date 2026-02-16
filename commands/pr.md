---
description: Create a GitHub pull request from the current branch with optional version bump and Copilot review
argument-hint: [--bump patch|minor|major] [--no-copilot] [--draft]
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, AskUserQuestion, Task, Skill
model: sonnet
---

<objective>
Orchestrate the full PR shipping workflow: commit → version bump → push → PR → Copilot review.

Delegates to `/commit` for staging/committing changes and to the **github** skill
for PR creation and Copilot review patterns (see the skill's `references/pr-workflow.md`).

**Flags:**

- *(no args)* - Commit pending changes, push, create PR
- `--bump patch|minor|major` - Bump version before PR (checks AGENTS.md for version file locations)
- `--no-copilot` - Skip waiting for Copilot review
- `--draft` - Create as draft PR

**Examples:**

- `/pr` - Commit, push, create PR, check Copilot
- `/pr --bump minor` - Bump version, commit, push, create PR
- `/pr --draft --no-copilot` - Quick draft PR, no review wait
</objective>

<context>
Current branch: !`git branch --show-current`
Default branch: !`git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}' || echo main`
Uncommitted changes: !`git status --short`
Unpushed commits: !`git log @{upstream}..HEAD --oneline 2>/dev/null || git log --oneline -5`
AGENTS.md version info: !`grep -i 'version' AGENTS.md 2>/dev/null | head -5 || echo "NO_AGENTS_MD"`
</context>

<process>

## Step 0: Safety Checks

1. **Branch check:** If on `main` or `master`, STOP. Ask user to create a feature branch first.
2. **Parse arguments:** Extract `--bump`, `--no-copilot`, `--draft` from `$ARGUMENTS`.

## Step 1: Handle Uncommitted Changes

If `git status --short` shows changes:

- Invoke `/commit` skill to stage and commit changes
- This handles staging, pre-commit hooks, and conventional commit message generation

If no uncommitted changes, skip to Step 2.

## Step 2: Version Bump (if --bump)

If `--bump` flag is present:

1. **Find version files:** Check `AGENTS.md` or `CLAUDE.md` for version file locations
2. **Read current version** from the source of truth
3. **Compute new version** (semver: patch/minor/major)
4. **Update ALL version files** in sync
5. **Commit:** `🔖 v<new>: <bump-type> version bump`

## Step 3: Push to Remote

```bash
git push -u origin $(git branch --show-current)
```

If push fails (e.g., diverged), show error and ask user how to proceed.

## Step 4: Create PR and Review

Follow the **github** skill's PR workflow (Steps 4-6 of its `references/pr-workflow.md`).
Locate the github skill's SKILL.md, then read `references/pr-workflow.md` relative to it:

1. Read the github skill's `references/pr-workflow.md` for PR creation patterns
2. Analyze all commits on the branch vs base branch
3. Create PR (pass `--draft` flag if requested)
4. Unless `--no-copilot`: follow the Copilot review steps from the workflow

</process>

<success_criteria>

- PR created on GitHub with descriptive title and body
- All version files bumped in sync (if --bump used)
- All commits pushed to remote
- Copilot feedback reviewed (unless --no-copilot)
- PR URL reported to user

</success_criteria>
