# PR Workflow

End-to-end workflow for shipping changes: branch, commit, version bump, PR, and Copilot review.

## Flow

```
Feature Branch ──▶ /commit ──▶ Version Bump ──▶ Push + PR ──▶ Copilot Review ──▶ Address Feedback
```

## Step 1: Create Feature Branch

```bash
git checkout -b <type>/<description>
```

Branch naming conventions:

| Type | Use |
|------|-----|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `refactor/` | Code restructuring |
| `chore/` | Tooling, config, dependencies |

## Step 2: Commit Changes

Use `/commit` to stage, run pre-commit hooks, and create a conventional commit with emoji.

If `/commit` is not available, follow the project's commit conventions manually.

## Step 3: Version Bump (Optional)

Ask the user for bump type before proceeding.

| Bump | When | Example |
|------|------|---------|
| `patch` | Bug fixes, doc corrections | `2.0.0` → `2.0.1` |
| `minor` | New features, backward-compatible | `2.0.0` → `2.1.0` |
| `major` | Breaking changes | `2.0.0` → `3.0.0` |

**Process:**

1. Check `AGENTS.md` or `CLAUDE.md` for version file locations
2. Read current version from source of truth
3. Compute new version (semver)
4. Update **all** version files in sync
5. Commit: `🔖 v<new>: <bump-type> version bump`

## Step 4: Push and Create PR

```bash
git push -u origin <branch>
gh pr create --title "<emoji> <type>: <description>" --body "$(cat <<'EOF'
## Summary
- <key changes as bullet points>

## Test plan
- [ ] <verification steps>
EOF
)"
```

**PR title** should match the primary commit message style. Keep under 70 characters.

## Step 5: Review Copilot Comments

Wait a moment for Copilot to post its review, then fetch:

```bash
# Get inline review comments
gh api repos/{owner}/{repo}/pulls/<number>/comments \
  --jq '.[] | select(.user.login == "Copilot") | {path, line, body}'

# Get general PR comments
gh pr view <number> --comments --json comments \
  --jq '.comments[] | select(.author.login == "github-actions" or .author.login == "Copilot") | {author: .author.login, body}'
```

**Summarize by theme** — group related comments rather than listing individually. Common themes:

- Missing flags or options (e.g., `jq -r`)
- Overly absolute language that needs qualifying
- Missing error handling or edge cases
- Style/consistency issues

## Step 6: Address Feedback

For each theme, decide: fix, skip, or discuss.

1. Apply fixes across all affected files
2. Run pre-commit hooks
3. Commit: `📝 docs: address Copilot review feedback` (or appropriate type)
4. Push to update the PR

```bash
git add <files>
pre-commit run --all-files
git commit -m "<emoji> <type>: address Copilot review feedback"
git push
```

## Quick Reference

Full sequence for a typical docs/feature change:

```bash
# 1. Branch
git checkout -b docs/my-change

# 2. (make changes)

# 3. Commit
/commit

# 4. Version bump (if needed)
# Update version files per AGENTS.md, then:
git add <version-files>
git commit -m "🔖 v<new>: patch version bump"

# 5. PR
git push -u origin docs/my-change
gh pr create --title "..." --body "..."

# 6. Copilot review
gh api repos/{owner}/{repo}/pulls/<num>/comments --jq '...'
# Fix, commit, push
```
