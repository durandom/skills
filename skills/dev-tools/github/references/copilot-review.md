# Copilot Code Review

Patterns for using GitHub Copilot as a **PR reviewer** (separate from Copilot Coding Agent — see `copilot-workflow.md` for that).

## When to Request Copilot Review

- **Before human review** — first pass for style, obvious bugs, security patterns
- **Quick sanity check** — small changes where full human review is overkill
- **Supplement human review** — extra coverage on top of a human reviewer

## Requesting Review

Three methods, simplest → most automated.

### 1. CLI (ad-hoc)

Requires `gh` v2.88.0+.

```bash
# Add Copilot as reviewer to existing PR
gh pr edit <number> --repo <owner>/<repo> --add-reviewer @copilot

# When creating a new PR
gh pr create --repo <owner>/<repo> --reviewer @copilot
```

### 2. gh extension (deduplicating)

Skips if already requested, hides outdated comments.

```bash
gh extension install k1LoW/gh-copilot-review

# Note: extension takes a URL, not --repo
gh copilot-review https://github.com/<owner>/<repo>/pull/<number>
```

### 3. Raw API

```bash
gh api --method POST /repos/<owner>/<repo>/pulls/<number>/requested_reviewers \
  -f "reviewers[]=copilot-pull-request-reviewer[bot]"
```

### 4. Org-Level Ruleset (automatic)

Configure in **Organization Settings → Rules → Rulesets**:

- Rule: "Automatic Copilot code review"
- Enable "Review new pushes" to re-review on each push

This is the **only** path that supports automatic re-review after Copilot has already submitted a review.

## Checking Copilot Feedback

```bash
# Review summary
gh pr view <number> --repo <owner>/<repo> --json reviews \
  --jq '.reviews[] | select(.author.login | test("copilot"; "i")) | {state, body}'

# Inline comments
gh api repos/<owner>/<repo>/pulls/<number>/comments \
  --jq '.[] | select(.user.login | test("copilot"; "i")) | {path, line, body}'

# Has Copilot reviewed yet? (count)
gh api repos/<owner>/<repo>/pulls/<number>/reviews \
  --jq '[.[] | select(.user.login | test("copilot"; "i"))] | length'
```

## Re-requesting Review

After addressing feedback:

| Method | Re-review supported? |
|--------|----------------------|
| Org Ruleset with "Review new pushes" | ✅ Automatic on push |
| Browser refresh icon next to Copilot | ✅ Manual |
| CLI / API re-request | ❌ No-op once Copilot has reviewed once |

See [community discussion #186152](https://github.com/orgs/community/discussions/186152) for the API limitation.

## Copilot vs. Human Review

| Aspect | Copilot | Human |
|--------|---------|-------|
| Speed | Minutes | Hours/days |
| Strengths | Style, mechanical bugs, security patterns | Architecture, design intent, business logic |
| Weaknesses | Misses context, false positives | Slower, may miss mechanical issues |
| Use for | First pass, small PRs, sanity checks | Pre-merge gate, architectural changes |

**Recommended flow:** Copilot first → address feedback → human review (focused on higher-level concerns).

## Cost

Each Copilot review = 1 premium request. With "Review new pushes" enabled, every push consumes another request — watch quota on busy PRs.

## CI Status Caveat

`gh pr checks` can lag behind the latest commit. To verify CI is actually green:

```bash
gh run list --repo <owner>/<repo> --branch <branch> --limit 1 --json conclusion,status
```
