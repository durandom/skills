---
description: Create a GitHub pull request from the current branch with optional version bump and Copilot review
argument-hint: [--bump patch|minor|major] [--no-copilot] [--draft]
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, AskUserQuestion, Task, Skill
model: sonnet
---

<objective>
Create a GitHub pull request from the current branch. Handles: uncommitted changes, version bumps, pushing, PR creation, and optional Copilot review.

**Flags:**

- *(no args)* - Commit pending changes, push, create PR
- `--bump patch|minor|major` - Bump version before PR (checks AGENTS.md for version file locations)
- `--no-copilot` - Skip waiting for Copilot review
- `--draft` - Create as draft PR

**Examples:**

- `/pr` - Commit, push, create PR, check Copilot
- `/pr --bump minor` - Bump version, commit, push, create PR
- `/pr --draft` - Create a draft PR
- `/pr --bump patch --no-copilot` - Bump, PR, skip Copilot review
</objective>

<context>
Current branch: !`git branch --show-current`
Default branch: !`git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}' || echo main`
Remote tracking: !`git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo "NO_UPSTREAM"`
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

1. Use the `/commit` skill to stage and commit changes:
   - Invoke: `Skill tool with skill: "commit"`
   - This handles staging, pre-commit hooks, and conventional commit message

If no uncommitted changes, skip to Step 2.

## Step 2: Version Bump (if --bump)

If `--bump` flag is present:

1. **Find version files:** Check `AGENTS.md` or `CLAUDE.md` for version file locations
2. **Read current version** from the source of truth
3. **Compute new version** using semver rules:
   - `patch`: 2.2.0 → 2.2.1
   - `minor`: 2.2.0 → 2.3.0
   - `major`: 2.2.0 → 3.0.0
4. **Update ALL version files** in sync (check AGENTS.md for locations)
5. **Commit version bump:**

   ```bash
   git add <version-files>
   git commit -m "$(cat <<'VEOF'
   🔖 v<new>: <bump-type> version bump
   VEOF
   )"
   ```

## Step 3: Push to Remote

```bash
git push -u origin $(git branch --show-current)
```

If push fails (e.g., diverged), show error and ask user how to proceed.

## Step 4: Create Pull Request

1. **Analyze all commits** on this branch vs base branch:

   ```bash
   git log $(git merge-base HEAD <default-branch>)..HEAD --oneline
   git diff $(git merge-base HEAD <default-branch>)..HEAD --stat
   ```

2. **Generate PR title:**
   - Match the primary commit's style (emoji + type)
   - Keep under 70 characters
   - If single commit: use its message
   - If multiple commits: summarize the theme

3. **Generate PR body:**
   - Summary section with key changes as bullet points
   - Test plan section with verification steps

4. **Create PR:**

   ```bash
   gh pr create \
     --title "<title>" \
     --body "$(cat <<'EOF'
   ## Summary
   - <key changes>

   ## Test plan
   - [ ] <verification steps>
   EOF
   )" \
     $( [ "$DRAFT" = true ] && echo "--draft" )
   ```

5. **Report PR URL** to user.

## Step 5: Copilot Review (unless --no-copilot)

1. **Wait briefly** (5-10 seconds) for Copilot to post its review
2. **Fetch Copilot comments:**

   ```bash
   # Get PR number
   PR_NUM=$(gh pr view --json number --jq .number)

   # Get owner/repo
   REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)

   # Inline review comments
   gh api repos/$REPO/pulls/$PR_NUM/comments \
     --jq '.[] | select(.user.login == "Copilot") | {path, line, body}'

   # General comments
   gh pr view $PR_NUM --comments --json comments \
     --jq '.comments[] | select(.author.login == "Copilot" or .author.login == "github-actions") | {author: .author.login, body}'
   ```

3. **If Copilot posted comments:**
   - Summarize by theme (group related comments)
   - Use AskUserQuestion:
     - "Address Copilot feedback" - Fix issues, commit, push
     - "Skip feedback" - Leave PR as-is
     - "Show raw comments" - Display full Copilot output

4. **If addressing feedback:**
   - Fix issues across affected files
   - Use `/commit` skill to commit fixes
   - Push to update PR

5. **If no Copilot comments found:** Report "No Copilot feedback" and finish.

</process>

<success_criteria>

- PR created on GitHub with descriptive title and body
- All version files bumped in sync (if --bump used)
- All commits pushed to remote
- Copilot feedback reviewed (unless --no-copilot)
- PR URL reported to user

</success_criteria>
