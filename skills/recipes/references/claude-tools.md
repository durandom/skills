# Recipe: Claude Code Tools Reference

**Target Audience:** AI Coding Agents, Skill/Command authors
**Goal:** Complete reference for all Claude Code native tools — parameters, capabilities, and coordination patterns.

> **⚠️ Freshness Warning:** Tool definitions change over time. When consuming this reference, **always cross-check against your current system prompt** — it contains the authoritative tool schemas for your session. This document provides patterns, best practices, and context that the system prompt does not, but parameter tables here may lag behind the actual tool definitions. If there is a conflict, **your system prompt wins**.

---

## Tool Inventory

Claude Code provides 20 built-in tools, plus an experimental multi-session coordination system:

| Category | Tools | Purpose |
|----------|-------|---------|
| **File Operations** | Read, Edit, Write, Glob, Grep, NotebookEdit | Navigate and modify code |
| **Execution** | Bash | Run shell commands |
| **Task Tracking** | TaskCreate, TaskUpdate, TaskList, TaskGet | Coordinate work, track progress |
| **Agent Spawning** | Task, TaskOutput, TaskStop | Launch and manage subagents |
| **Web** | WebFetch, WebSearch | Retrieve external information |
| **Interaction** | AskUserQuestion, EnterPlanMode, ExitPlanMode, Skill | User communication and planning |
| **Agent Teams** ⚠️ | *(natural language, not tool-based)* | Multi-session coordination (experimental) |

---

## File Operations

### Read

Read files from the filesystem. Supports text, images, PDFs, and Jupyter notebooks.

| Field | Required | Description |
|-------|----------|-------------|
| `file_path` | Yes | Absolute path to the file |
| `offset` | No | Line number to start reading from |
| `limit` | No | Number of lines to read (default: up to 2000) |
| `pages` | No | Page range for PDFs (e.g., `"1-5"`). Required for PDFs >10 pages |

**Notes:**

- Lines longer than 2000 characters are truncated
- Output uses `cat -n` format (line numbers starting at 1)
- Can read images (PNG, JPG, etc.) — content is presented visually
- PDFs: max 20 pages per request

---

### Edit

Exact string replacement in files. Must `Read` the file first.

| Field | Required | Description |
|-------|----------|-------------|
| `file_path` | Yes | Absolute path to the file |
| `old_string` | Yes | Text to find (must be unique in file) |
| `new_string` | Yes | Replacement text (must differ from old_string) |
| `replace_all` | No | Replace all occurrences (default: `false`) |

**Notes:**

- Fails if `old_string` is not unique — provide more surrounding context or use `replace_all`
- Use `replace_all` for renaming variables/strings across a file

---

### Write

Create or overwrite a file. Must `Read` existing files first.

| Field | Required | Description |
|-------|----------|-------------|
| `file_path` | Yes | Absolute path (must be absolute, not relative) |
| `content` | Yes | Full file content |

---

### Glob

Fast file pattern matching. Returns paths sorted by modification time.

| Field | Required | Description |
|-------|----------|-------------|
| `pattern` | Yes | Glob pattern (e.g., `**/*.ts`, `src/**/*.test.js`) |
| `path` | No | Directory to search in (default: cwd) |

---

### Grep

Content search powered by ripgrep. Supports regex, file filtering, and context lines.

| Field | Required | Description |
|-------|----------|-------------|
| `pattern` | Yes | Regex pattern to search for |
| `path` | No | File or directory to search (default: cwd) |
| `glob` | No | Filter files by glob (e.g., `*.js`) |
| `type` | No | File type filter (e.g., `js`, `py`, `rust`) |
| `output_mode` | No | `files_with_matches` (default), `content`, or `count` |
| `-A` / `-B` / `-C` / `context` | No | Lines after / before / around each match (`context` is an alias for `-C`) |
| `-i` | No | Case insensitive |
| `-n` | No | Show line numbers (default: `true`) |
| `multiline` | No | Match patterns across lines |
| `head_limit` | No | Limit output to first N entries |
| `offset` | No | Skip first N entries |

**Notes:**

- Uses ripgrep syntax — literal braces need escaping (e.g., `interface\{\}`)
- Prefer `type` over `glob` for standard file types (more efficient)

---

### NotebookEdit

Edit Jupyter notebook cells (.ipynb files).

| Field | Required | Description |
|-------|----------|-------------|
| `notebook_path` | Yes | Absolute path to .ipynb file |
| `new_source` | Yes | New cell source content |
| `cell_id` | No | Cell ID to edit (for insert: new cell goes after this) |
| `cell_type` | No | `code` or `markdown` (required for insert) |
| `edit_mode` | No | `replace` (default), `insert`, or `delete` |

---

## Execution

### Bash

Execute shell commands with optional timeout and background execution.

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes | The command to execute |
| `description` | No | What the command does (for clarity) |
| `timeout` | No | Max wait in ms (default: 120000, max: 600000) |
| `run_in_background` | No | Run async; use `TaskOutput` to check results later |
| `dangerouslyDisableSandbox` | No | Override sandbox mode. Avoid unless absolutely necessary — prefer working within the sandbox |

**Notes:**

- Working directory persists between calls; shell state does not
- Output truncated at 30000 characters
- Prefer dedicated tools over Bash for file operations (Read not cat, Edit not sed, Grep not grep, etc.)
- Commands run in a sandbox by default; `dangerouslyDisableSandbox` exists but should rarely be needed

---

## Web Tools

### WebFetch

Fetch a URL, convert HTML to markdown, and analyze content with a prompt.

| Field | Required | Description |
|-------|----------|-------------|
| `url` | Yes | Fully-formed URL (HTTP auto-upgrades to HTTPS) |
| `prompt` | Yes | What to extract from the page content |

**Notes:**

- Will fail on authenticated/private URLs (Google Docs, Jira, etc.)
- 15-minute cache for repeated fetches
- Large content may be summarized

---

### WebSearch

Search the web. Returns results with links.

| Field | Required | Description |
|-------|----------|-------------|
| `query` | Yes | Search query |
| `allowed_domains` | No | Only include results from these domains |
| `blocked_domains` | No | Exclude results from these domains |

---

## Interaction & Planning

### AskUserQuestion

Present structured questions with selectable options.

| Field | Required | Description |
|-------|----------|-------------|
| `questions` | Yes | Array of 1–4 questions |
| `answers` | No | User answers collected by the permission component (internal) |
| `metadata` | No | Tracking metadata (e.g., `{ "source": "remember" }` for analytics) |

Each question:

| Field | Required | Description |
|-------|----------|-------------|
| `question` | Yes | The question text |
| `header` | Yes | Short label (max 12 chars) shown as chip/tag |
| `options` | Yes | 2–4 options, each with `label` and `description` |
| `multiSelect` | Yes | Allow multiple selections (default: `false`) |

Users can always select "Other" to provide custom text.

---

### EnterPlanMode

Transition into plan mode for designing an implementation approach before writing code. No parameters.

Use for non-trivial tasks where approach alignment matters before implementation.

---

### ExitPlanMode

Signal that your plan is complete and ready for user review. No required parameters.

| Field | Required | Description |
|-------|----------|-------------|
| `allowedPrompts` | No | Array of `{tool, prompt}` permission pairs needed for implementation |
| `pushToRemote` | No | Push plan to a remote Claude.ai session |
| `remoteSessionId` | No | Remote session ID if pushed |
| `remoteSessionTitle` | No | Remote session title if pushed |
| `remoteSessionUrl` | No | Remote session URL if pushed |

---

### Skill

Execute a registered skill (slash command).

| Field | Required | Description |
|-------|----------|-------------|
| `skill` | Yes | Skill name (e.g., `commit`, `review-pr`) |
| `args` | No | Arguments for the skill |

---

## Task Tracking

Four tools for work coordination, progress tracking, and context recovery. Tasks are **persistent within the session** — they survive context compaction.

Users see task progress via `ctrl+t`:

```
Tasks (2 done, 2 in progress, 3 open)
✓ #1 Setup database schema
■ #2 Implement auth middleware (Worker-1)
■ #3 Add login route (Worker-2)
□ #4 Add protected routes > blocked by #2
□ #5 Run exit criteria > blocked by #2, #3, #4
```

### TaskCreate

Creates a new task. All tasks start as `pending`.

```json
TaskCreate({
  "subject": "Implement auth middleware",
  "description": "Create JWT validation middleware in src/middleware/auth.ts...",
  "activeForm": "Implementing auth middleware"
})
```

| Field | Required | Description |
|-------|----------|-------------|
| `subject` | Yes | Brief title (imperative: "Add tests", "Fix bug") |
| `description` | Yes | Full details — should be self-contained |
| `activeForm` | No | Present continuous for spinner ("Adding tests") |
| `metadata` | No | Arbitrary key-value pairs for tracking |

**Best practices:**

- Make descriptions self-contained — another agent should understand without context
- Use imperative mood for subjects ("Run tests" not "Running tests")
- Use present continuous for activeForm ("Running tests" not "Run tests")

---

### TaskUpdate

Update status, owner, dependencies, or content of a task.

```json
TaskUpdate({
  "taskId": "1",
  "status": "in_progress",
  "owner": "Worker-1"
})
```

| Field | Required | Description |
|-------|----------|-------------|
| `taskId` | Yes | Task ID to update |
| `status` | No | `pending` → `in_progress` → `completed` (or `deleted`) |
| `owner` | No | Agent name claiming the task |
| `addBlockedBy` | No | Array of task IDs that block this one |
| `addBlocks` | No | Array of task IDs this task blocks |
| `subject` | No | Update the title |
| `description` | No | Update the description |
| `activeForm` | No | Update the spinner text (present continuous) |
| `metadata` | No | Merge key-value pairs (set key to `null` to delete) |

**Status workflow:**

```
pending → in_progress → completed
any status → deleted  (permanently removes the task)
```

**Setting dependencies:**

```json
TaskUpdate({
  "taskId": "3",
  "addBlockedBy": ["1", "2"]
})
```

This means task #3 cannot start until #1 and #2 are completed.

---

### TaskList

Returns a summary of all tasks. No parameters.

```json
TaskList({})
```

**Returns:**

```
id: 1 | subject: "Setup database" | status: completed | owner: Worker-1
id: 2 | subject: "Auth middleware" | status: in_progress | owner: Worker-2
id: 3 | subject: "Login routes" | status: pending | blockedBy: [2]
```

Use this to:

- Find available work (pending, no owner, empty blockedBy)
- Check overall progress
- Recover context after compaction

---

### TaskGet

Fetch full details for a specific task.

```json
TaskGet({
  "taskId": "1"
})
```

**Returns:** Full task including subject, description, status, owner, blockedBy, blocks.

Use before starting work to get the complete requirements.

---

## Agent Spawning

Three tools for launching, monitoring, and stopping subagents.

### Task

Launch a specialized subagent to handle a task autonomously.

```json
Task({
  "description": "Search auth patterns",
  "prompt": "Find all authentication middleware and summarize the patterns used.",
  "subagent_type": "Explore"
})
```

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | Short summary (3–5 words) |
| `prompt` | Yes | Full instructions for the agent |
| `subagent_type` | Yes | Agent type (see table below) |
| `model` | No | `sonnet`, `opus`, or `haiku` (inherits from parent) |
| `run_in_background` | No | Run asynchronously (`true` for parallel work) |
| `max_turns` | No | Cap on API round-trips |
| `resume` | No | Agent ID to continue previous work with full context |

**Built-in agent types:**

| Type | Tools Available | Best For |
|------|----------------|----------|
| `Bash` | Bash only | Git operations, command execution |
| `general-purpose` | All tools | Multi-step implementation, swarm workers |
| `Explore` | Read-only tools | Fast codebase search and understanding |
| `Plan` | Read-only tools | Architecture design, implementation planning |
| `statusline-setup` | Read, Edit | Configure Claude Code status line settings |

> **Plugin-provided agent types:** Plugins and skills can register additional subagent types (e.g., `essentials:plan-creator-default`, `essentials:bug-plan-creator-default`, `tcrd:slash-command-auditor`). These appear in your system prompt alongside the built-in types. Check your system prompt's Task tool description for the full list available in your session.

**Notes:**

- Background agents return an `output_file` path — use `Read` or `TaskOutput` to check
- `resume` continues an agent with full previous context preserved
- Launch multiple agents in parallel by making multiple `Task` calls in one message
- Prefer `haiku` for quick tasks, `sonnet` for implementation, `opus` for complex reasoning
- Agent results are returned to the caller, not shown directly to the user

---

### TaskOutput

Retrieve output from a running or completed background task.

```json
TaskOutput({
  "task_id": "abc-123",
  "block": true,
  "timeout": 30000
})
```

| Field | Required | Description |
|-------|----------|-------------|
| `task_id` | Yes | ID of the background task |
| `block` | No | Wait for completion (default: `true`) |
| `timeout` | No | Max wait in ms (default: 30000, max: 600000) |

Use `block: false` for non-blocking status checks.

---

### TaskStop

Stop a running background task.

```json
TaskStop({
  "task_id": "abc-123"
})
```

| Field | Required | Description |
|-------|----------|-------------|
| `task_id` | Yes | ID of the background task to stop |

---

### Communication Model

Subagent communication is **unidirectional and fire-and-forget**. Understanding this constraint is critical for designing agent workflows.

```
┌──────────────┐   prompt    ┌──────────────┐
│  Main Agent  │ ──────────► │   Subagent   │
│              │             │              │
│              │ ◄────────── │  (runs autonomously)
│              │   result    │              │
└──────────────┘  (single)   └──────────────┘
```

**What subagents CAN do:**

- Run autonomously using their available tools
- Ask the **user** directly via `AskUserQuestion` (`general-purpose` type only)
- Return a single result message when finished

**What subagents CANNOT do:**

- Pause mid-execution to ask the parent agent a question
- Send progress updates or partial results back to the parent
- Receive new instructions while running (except via `TaskStop` to cancel)

**Multi-turn follow-up via `resume`:**

The `resume` parameter enables multi-turn conversations with a subagent, but the **parent always initiates** each turn:

```
Turn 1:  Main ──prompt──►  Subagent  ──result──►  Main
         Main inspects result, decides follow-up needed
Turn 2:  Main ──resume(id) + new prompt──►  Same Subagent (full context)  ──result──►  Main
```

The subagent retains its full conversation history across resumes, so it doesn't lose context. But it cannot request a resume — only the parent can.

**Implications for workflow design:**

- Give subagents **complete, self-contained prompts** — they can't ask for clarification
- For tasks requiring back-and-forth discussion, use **Agent Teams** instead
- Use `run_in_background` + `TaskOutput` for monitoring, but this only checks completion — not mid-flight status
- If a subagent needs decisions, have it return options and let the parent decide, then `resume`

---

## Agent Teams (Experimental)

> **Source:** https://code.claude.com/docs/en/agent-teams
>
> ⚠️ **Experimental — disabled by default.** Enable via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in environment or settings.json. Has known limitations around session resumption, task coordination, and shutdown behavior.

Agent Teams coordinate **multiple independent Claude Code sessions** working together. One session is the team lead; the rest are teammates. Unlike subagents (which run inside a single session), teammates are full Claude Code instances that can message each other directly.

### Subagents vs Agent Teams

|                   | Subagents (`Task` tool)                          | Agent Teams                                         |
| :---------------- | :----------------------------------------------- | :-------------------------------------------------- |
| **Context**       | Own context window; results return to caller     | Own context window; fully independent               |
| **Communication** | Report results back to main agent only           | Teammates message each other directly               |
| **Coordination**  | Main agent manages all work                      | Shared task list with self-coordination             |
| **Best for**      | Focused tasks where only the result matters      | Complex work requiring discussion and collaboration |
| **Token cost**    | Lower: results summarized back to main context   | Higher: each teammate is a separate Claude instance |

**Rule of thumb:** Use subagents when workers just need to report back. Use agent teams when teammates need to share findings, challenge each other, and coordinate on their own.

### Enabling

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Architecture

| Component      | Role |
|:---------------|:-----|
| **Team lead**  | Main session — creates team, spawns teammates, coordinates work |
| **Teammates**  | Separate Claude Code instances working on assigned tasks |
| **Task list**  | Shared task list (uses TaskCreate/TaskUpdate/TaskList/TaskGet) |
| **Mailbox**    | Messaging system for inter-agent communication |

Team config: `~/.claude/teams/{team-name}/config.json`
Task list: `~/.claude/tasks/{team-name}/`

### Starting a Team

Teams are created via natural language — there is no dedicated tool. The lead spawns teammates based on your prompt:

```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
```

### Key Capabilities

**Display modes:**

| Mode | How | When |
|------|-----|------|
| `in-process` | All teammates in main terminal. `Shift+Up/Down` to select. | Default; any terminal |
| `tmux` / `iTerm2` | Each teammate gets its own split pane | Requires tmux or iTerm2 |

Override with `--teammate-mode in-process` or `teammateMode` in settings.json.

**Delegate mode:** Press `Shift+Tab` to restrict the lead to coordination-only — it can spawn, message, and manage tasks but cannot write code. Useful when you want the lead focused on orchestration.

**Plan approval:** Require teammates to plan before implementing. The lead reviews and approves/rejects plans before teammates can write code:

```
Spawn an architect teammate to refactor the auth module.
Require plan approval before they make any changes.
```

**Direct interaction:** Message any teammate directly — not just through the lead. In in-process mode, use `Shift+Up/Down` to select a teammate and type.

### Task Coordination

Agent Teams use the same TaskCreate/TaskUpdate/TaskList/TaskGet tools documented above. The shared task list coordinates work:

- Lead creates tasks and assigns them to teammates
- Teammates can self-claim unassigned, unblocked tasks
- Task claiming uses file locking to prevent race conditions
- Dependencies auto-unblock when prerequisite tasks complete

### Hooks for Quality Gates

| Hook | Fires when | Use |
|------|-----------|-----|
| `TeammateIdle` | Teammate about to go idle | Exit code 2 sends feedback, keeps teammate working |
| `TaskCompleted` | Task being marked complete | Exit code 2 prevents completion, sends feedback |

### Known Limitations

- **No session resumption** for in-process teammates — `/resume` and `/rewind` don't restore them
- **Task status can lag** — teammates sometimes fail to mark tasks complete
- **One team per session** — clean up before starting a new team
- **No nested teams** — teammates cannot spawn their own teams
- **Lead is fixed** — cannot transfer leadership to a teammate
- **Permissions set at spawn** — all teammates inherit the lead's permission mode
- **Split panes** require tmux or iTerm2 (not VS Code terminal, Windows Terminal, or Ghostty)
- **Shutdown can be slow** — teammates finish current work before exiting

### Best Practices

- **Give enough context** in spawn prompts — teammates don't inherit the lead's conversation history
- **Size tasks appropriately** — 5-6 tasks per teammate keeps everyone productive
- **Avoid file conflicts** — break work so each teammate owns different files
- **Start with research/review** — lower coordination risk than parallel implementation
- **Monitor and steer** — check in on progress, redirect approaches that aren't working

---

## Coordination Patterns

### Pattern 1: Sequential Execution (Loop)

A single agent processes tasks one at a time in dependency order.

```
┌─────────────────────────────────────────────────────┐
│  LOOP:                                              │
│  1. TaskList → find pending, unblocked tasks        │
│  2. TaskUpdate → claim (status: in_progress)        │
│  3. Execute the work                                │
│  4. TaskUpdate → complete (status: completed)       │
│  5. GOTO 1                                          │
│                                                     │
│  STOP: All tasks completed                          │
└─────────────────────────────────────────────────────┘
```

**When to use:**

- Debugging (easier to follow)
- Cost-sensitive (single context)
- Linear dependencies (no parallelism benefit)

---

### Pattern 2: Parallel Execution (Swarm)

Multiple worker agents coordinate via the Task tracking system.

```
┌─────────────────────────────────────────────────────┐
│  Worker-N LOOP:                                     │
│  1. TaskList → find all tasks                       │
│  2. Filter: pending, no owner, blockedBy completed  │
│  3. TaskUpdate → claim (owner: Worker-N, in_progress)│
│  4. Execute the work                                │
│  5. TaskUpdate → complete                           │
│  6. GOTO 1                                          │
│                                                     │
│  STOP: All tasks completed OR no claimable tasks    │
│  CONFLICT: Skip if already claimed, find next       │
└─────────────────────────────────────────────────────┘
```

**Spawning workers:**

```json
// Launch workers in parallel (single message, multiple Task calls)
Task({
  "description": "Worker-1 executor",
  "subagent_type": "general-purpose",
  "model": "sonnet",
  "run_in_background": true,
  "prompt": "You are Worker-1 in a parallel swarm.\n\nLOOP:\n1. TaskList - find all tasks\n2. Filter: pending, no owner, blockedBy all completed\n3. TaskUpdate - claim: owner: Worker-1, status: in_progress\n4. Execute task per description\n5. TaskUpdate - status: completed\n6. GOTO 1\n\nSTOP WHEN: All tasks completed OR no claimable tasks remain\nCONFLICT: If already claimed by another, skip and find next"
})

Task({
  "description": "Worker-2 executor",
  "subagent_type": "general-purpose",
  "model": "sonnet",
  "run_in_background": true,
  "prompt": "You are Worker-2 in a parallel swarm.\n\n[same loop instructions with owner: Worker-2]"
})
```

**Optimistic locking:** Workers check `owner` field — if another worker claimed it first, back off and find the next task.

**Calculating worker count:**

```
1. Build dependency graph from blockedBy arrays
2. Find maximum width (most concurrent unblocked tasks at any point)
3. Worker count = min(max_width, 10)  # Cap to avoid overload
```

If graph is fully linear (A→B→C→D), max width = 1, so swarm degrades to loop behavior.

**When to use:**

- Many independent tasks
- Wide dependency graph (high parallelism)
- Speed is priority over cost

---

### Pattern 3: Building a Task Graph

Convert a plan into tasks with dependencies.

```json
// Create tasks
TaskCreate({ "subject": "Create auth middleware", "description": "...", "activeForm": "Creating auth middleware" })
TaskCreate({ "subject": "Create login routes", "description": "...", "activeForm": "Creating login routes" })
TaskCreate({ "subject": "Create profile routes", "description": "...", "activeForm": "Creating profile routes" })

// Set dependencies (login and profile both depend on auth)
TaskUpdate({ "taskId": "2", "addBlockedBy": ["1"] })
TaskUpdate({ "taskId": "3", "addBlockedBy": ["1"] })
```

**Resulting graph:**

```
auth.ts (#1)
    ↓
 ┌──┴──┐
 ↓     ↓
login  profile  ← Run in parallel (both only blocked by #1)
(#2)   (#3)
```

---

### Pattern 4: Context Recovery

When conversation context compacts, recover state from tasks.

```
If context compacts:
1. TaskList → see all tasks and their status
2. Re-read the plan file
3. Find next pending unblocked task
4. Continue implementation
```

The Task tracking system is **persistent within the session** — even if the conversation summary loses details, `TaskList` retains the full state.

---

### Pattern 5: Exit Criteria Task

Create a final verification task blocked by all implementation tasks.

```json
TaskCreate({
  "subject": "Run exit criteria",
  "description": "Run verification: npm test && npm run lint && npm run typecheck",
  "activeForm": "Running exit criteria"
})
TaskUpdate({
  "taskId": "5",
  "addBlockedBy": ["1", "2", "3", "4"]
})
```

This ensures verification only runs after all work completes.

---

### Pattern 6: Parallel Research

Use multiple `Explore` agents to investigate different aspects simultaneously.

```json
// Launch in parallel (single message, multiple Task calls)
Task({
  "description": "Find auth patterns",
  "subagent_type": "Explore",
  "prompt": "Find all authentication middleware and summarize patterns."
})

Task({
  "description": "Find test patterns",
  "subagent_type": "Explore",
  "prompt": "Find the testing patterns used in this project."
})
```

Results return to the orchestrating agent for synthesis.

---

### Pattern 7: Agent Team (Experimental)

When work requires inter-agent discussion or competing perspectives, use Agent Teams instead of subagents.

```
Create an agent team to investigate the performance regression:
- One teammate profiles the API layer
- One teammate analyzes database queries
- One teammate checks for memory leaks
Have them share findings and challenge each other's conclusions.
```

**Key difference from Pattern 2 (Swarm):** Swarm workers are subagents that report back to a single orchestrator. Agent Team teammates are independent sessions that communicate directly with each other.

**When to use Agent Teams over Subagents:**

| Scenario | Use |
|----------|-----|
| Workers just produce results | Subagents (Pattern 2) |
| Workers need to discuss and coordinate | Agent Teams |
| Quick, focused parallel tasks | Subagents |
| Cross-layer changes (frontend + backend + tests) | Agent Teams |
| Debugging with competing hypotheses | Agent Teams |
| Cost-sensitive | Subagents (lower token usage) |

---

## Anti-Patterns

### Don't create tasks without descriptions

```json
// BAD: Another agent can't understand this
TaskCreate({ "subject": "Fix the thing" })

// GOOD: Self-contained description
TaskCreate({
  "subject": "Fix null pointer in user lookup",
  "description": "In src/services/user.ts:42, add null check before accessing user.profile..."
})
```

### Don't forget dependencies

```json
// BAD: Tasks run in wrong order
TaskCreate({ "subject": "Deploy to prod" })  // #1
TaskCreate({ "subject": "Run tests" })       // #2 — should block #1!

// GOOD: Explicit dependencies
TaskCreate({ "subject": "Run tests" })       // #1
TaskCreate({ "subject": "Deploy to prod" })  // #2
TaskUpdate({ "taskId": "2", "addBlockedBy": ["1"] })
```

### Don't mark tasks complete prematurely

Only mark completed when FULLY done. If blocked or errored:

- Keep as `in_progress`
- Create a new task for the blocker

Never mark completed if: tests failing, partial implementation, unresolved errors.

### Don't create circular dependencies

```json
// BAD: Deadlock — neither can start
TaskUpdate({ "taskId": "1", "addBlockedBy": ["2"] })
TaskUpdate({ "taskId": "2", "addBlockedBy": ["1"] })
```

### Don't use Bash for file operations

```json
// BAD
Bash({ "command": "cat src/main.ts" })
Bash({ "command": "grep -r 'TODO' src/" })

// GOOD — use dedicated tools
Read({ "file_path": "src/main.ts" })
Grep({ "pattern": "TODO", "path": "src/" })
```

---

## Tool Selection Guide

| I need to... | Use |
|--------------|-----|
| Read a file | `Read` |
| Find files by name/pattern | `Glob` |
| Search file contents | `Grep` |
| Make targeted edits | `Edit` |
| Create a new file | `Write` |
| Edit a Jupyter notebook | `NotebookEdit` |
| Run a shell command | `Bash` |
| Search the web | `WebSearch` |
| Fetch and analyze a URL | `WebFetch` |
| Track multi-step work | `TaskCreate` + `TaskUpdate` |
| Spawn a helper agent | `Task` |
| Run agents in parallel | `Task` with `run_in_background: true` |
| Check on a background agent | `TaskOutput` |
| Cancel a background agent | `TaskStop` |
| Ask the user a question | `AskUserQuestion` |
| Plan before implementing | `EnterPlanMode` |
| Execute a skill | `Skill` |
| Coordinate independent sessions | Agent Teams ⚠️ (experimental) |

---

## Verification Protocol

> **For Claude agents consuming this document:** This reference is a point-in-time snapshot. Tool schemas evolve across Claude Code releases — parameters get added, renamed, or deprecated.
>
> **Before relying on any parameter table above:**
>
> 1. Check your **system prompt** — it contains the canonical tool definitions for your session
> 2. If a parameter listed here is absent from your system prompt, it may have been removed or renamed — **do not use it**
> 3. If your system prompt lists parameters not documented here, **prefer the system prompt** — this document may be outdated
> 4. The **patterns and best practices** in this document (coordination patterns, anti-patterns, tool selection guide) are more stable than parameter specifics and remain useful even when schemas drift
>
> When in doubt: system prompt > this document.
