---
description: Stage all changes, run pre-commit hooks, fix failures, and create conventional commit with emoji
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, AskUserQuestion
model: haiku
---

<objective>
Create a well-formatted git commit with conventional commit messages and emoji.

The workflow stages all changes, runs pre-commit hooks if available, fixes any failures,
gets user approval for agent-made changes, and generates a commit message that matches
the project's existing style.
</objective>

<context>
Git status: !`git status --short`
Recent commits (for style matching): !`git log --oneline -5`
Pre-commit config exists: !`test -f .pre-commit-config.yaml && echo "yes" || echo "no"`
Staged files: !`git diff --cached --name-only`
</context>

<process>

1. **Stage all changes**
   - Run `git add -A` to stage all modified, new, and deleted files

2. **Check for pre-commit hooks**
   - If `.pre-commit-config.yaml` exists, run `pre-commit run --all-files`
   - If pre-commit is not installed, skip this step

3. **Handle pre-commit failures**
   - If pre-commit fails, analyze the errors
   - Fix linting, formatting, and other auto-fixable issues
   - For non-auto-fixable issues, make the necessary code changes
   - After fixing, do NOT stage the fixes yet

4. **User approval for agent changes**
   - If any files were modified by pre-commit or by fixing failures:
     - Run `git diff` to show unstaged changes (these are the agent's fixes)
     - Use AskUserQuestion to ask user to review the diff
     - Options: "Approve changes" or "Reject and abort"
   - If rejected, run `git checkout -- .` to discard fixes and abort

5. **Stage fixes and analyze changes**
   - Run `git add -A` to stage all fixes
   - Use `git diff --stat --cached` for overview
   - For large diffs (>500 lines), use grep strategy (see below) instead of reading full diff
   - Use grep to quickly assess impact before reading files in detail
   - Only read full files when grep indicates significant changes

6. **Match project commit style**
   - Analyze recent commits for: language, emoji usage, format conventions
   - Follow the existing style (don't impose a standard)

7. **Generate commit message**
   - Use emoji conventional commit format: `<emoji> <type>: <description>`
   - First line < 72 characters, imperative mood, present tense
   - Focus on WHAT changed and WHY, not HOW
   - For complex changes, use multi-line format with bullet points
   - Consider if changes should be split into multiple commits

8. **Create the commit**
   - Run `git commit -m "<message>"` using HEREDOC for proper formatting
   - Verify commit was created successfully with `git log -1`

</process>

<commit_types>

- ✨ `feat`: New feature
- 🐛 `fix`: Bug fix
- 📝 `docs`: Documentation
- 💄 `style`: Formatting/style
- ♻️ `refactor`: Code refactoring
- ⚡️ `perf`: Performance improvements
- ✅ `test`: Tests
- 🔧 `chore`: Tooling, configuration
- 🚀 `ci`: CI/CD improvements
- 🚨 `fix`: Fix compiler/linter warnings
- 🔒️ `fix`: Fix security issues
- 🏗️ `refactor`: Architectural changes
- 🔥 `fix`: Remove code or files
- 🎨 `style`: Improve structure/format
- 💚 `fix`: Fix CI build
- ✏️ `fix`: Fix typos
</commit_types>

<splitting_guidance>
Consider splitting commits when changes touch:

- Different concerns (unrelated parts of codebase)
- Different types (mixing features, fixes, refactoring)
- Different file patterns (source vs docs vs config)
- Large changes that would be clearer if broken down

If splitting is needed, guide the user through selective staging with `git add -p` or file-by-file staging.
</splitting_guidance>

<grep_strategy>
Grep is faster than reading entire files. Use it to quickly assess impact before deciding which files to read in detail.

**Patterns for analyzing changes:**

- Find function/method calls: `grep -n "function_name("`
- Count occurrences to gauge scope: `grep -c "pattern" file`
- Get context around matches: `grep -C 3 "function_name"`
- Find all files with pattern: `grep -l "pattern" --include="*.py"`

**When to use grep vs full read:**

- Use grep first to identify which files have significant changes
- Read full file only when grep shows complex modifications
- For simple additions/deletions, grep context is often sufficient
- Prioritize reading files with highest match counts (most impactful)
</grep_strategy>

<success_criteria>

- All files staged appropriately
- Pre-commit hooks pass (if present)
- User approved any agent-made changes
- Commit message follows project conventions
- Commit message uses emoji conventional commit format
- Commit created successfully
- No uncommitted changes remain (unless intentionally excluded)
</success_criteria>

<verification>
After commit, verify:
- `git status` shows clean working directory
- `git log -1 --stat` shows expected changes
- Commit message is properly formatted
</verification>
