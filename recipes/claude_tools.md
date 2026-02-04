# Recipe: Claude Code Task Management Tools

**Target Audience:** AI Coding Agents, Skill/Command authors
**Goal:** Understand and effectively use Claude Code's native Task tools for coordinating work, tracking progress, and enabling parallel execution.

---

## Overview

Claude Code provides a built-in Task Management System with four core tools:

| Tool | Purpose |
|------|---------|
| `TaskCreate` | Create new tasks with dependencies |
| `TaskUpdate` | Update status, owner, and relationships |
| `TaskList` | List all tasks with summary info |
| `TaskGet` | Fetch full details for a specific task |

These tools enable:

- **Progress tracking** visible via `ctrl+t` in Claude Code
- **Dependency management** with `blockedBy` relationships
- **Parallel coordination** via owner-based claiming
- **Context recovery** when conversation compacts

---

## Tool Reference

### TaskCreate

Creates a new task. All tasks start with status `pending`.

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

Updates an existing task's status, owner, or dependencies.

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
| `status` | No | `pending` → `in_progress` → `completed` |
| `owner` | No | Agent name claiming the task |
| `addBlockedBy` | No | Array of task IDs that block this one |
| `addBlocks` | No | Array of task IDs this task blocks |
| `subject` | No | Update the title |
| `description` | No | Update the description |

**Status workflow:**

```
pending → in_progress → completed
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

Returns a summary of all tasks.

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

Fetches full details for a specific task.

```json
TaskGet({
  "taskId": "1"
})
```

**Returns:** Full task including subject, description, status, owner, blockedBy, blocks.

Use before starting work to get the complete requirements.

---

## Pattern 1: Sequential Execution (Loop)

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

**Example from essentials-claude-code `/plan-loop`:**

```markdown
### Step 3: Execute Tasks Sequentially

For each task (in dependency order):

1. **Claim**: `TaskUpdate({ taskId: "N", status: "in_progress" })`
2. **Read**: Get relevant section from plan
3. **Implement**: Make changes following plan exactly
4. **Verify**: Run any task-specific verification
5. **Complete**: `TaskUpdate({ taskId: "N", status: "completed" })`
6. **Next**: Find next unblocked task via TaskList
```

**When to use:**

- Debugging (easier to follow)
- Cost-sensitive (single context)
- Linear dependencies (no parallelism benefit)

---

## Pattern 2: Parallel Execution (Swarm)

Multiple worker agents coordinate via the Task system.

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

**Example from essentials-claude-code `/plan-swarm`:**

```json
Task({
  "description": "Worker-1 executor",
  "subagent_type": "general-purpose",
  "model": "sonnet",
  "run_in_background": true,
  "prompt": "You are Worker-1 in a parallel swarm.

LOOP:
1. TaskList - find all tasks
2. Filter: pending, no owner, blockedBy all completed
3. TaskUpdate - claim: owner: Worker-1, status: in_progress
4. Execute task per description
5. TaskUpdate - status: completed
6. GOTO 1

STOP WHEN: All tasks completed OR no claimable tasks remain
CONFLICT: If already claimed by another, skip and find next"
})
```

**Optimistic locking:** Workers check `owner` field — if another worker claimed it first, back off and find the next task.

**When to use:**

- Many independent tasks
- Wide dependency graph (high parallelism)
- Speed is priority over cost

---

## Pattern 3: Building a Task Graph

Convert a plan or prd.json into tasks with dependencies.

### Example: Plan with file dependencies

```markdown
### src/middleware/auth.ts [create]
**Dependencies**: None
**Provides**: `authMiddleware()`, `verifyToken()`

### src/routes/login.ts [create]
**Dependencies**: authMiddleware from auth.ts
**Provides**: `POST /login`

### src/routes/profile.ts [create]
**Dependencies**: authMiddleware from auth.ts
**Provides**: `GET /profile`
```

**Becomes:**

```json
// Task 1: No dependencies (root)
TaskCreate({
  "subject": "Create auth middleware",
  "description": "Create src/middleware/auth.ts with authMiddleware() and verifyToken()...",
  "activeForm": "Creating auth middleware"
})

// Task 2: Depends on Task 1
TaskCreate({
  "subject": "Create login routes",
  "description": "Create src/routes/login.ts with POST /login...",
  "activeForm": "Creating login routes"
})
TaskUpdate({ "taskId": "2", "addBlockedBy": ["1"] })

// Task 3: Also depends on Task 1 (parallel with Task 2!)
TaskCreate({
  "subject": "Create profile routes",
  "description": "Create src/routes/profile.ts with GET /profile...",
  "activeForm": "Creating profile routes"
})
TaskUpdate({ "taskId": "3", "addBlockedBy": ["1"] })
```

**Resulting graph:**

```
auth.ts (#1)
    ↓
 ┌──┴──┐
 ↓     ↓
login  profile  ← These run in parallel (both only blocked by #1)
(#2)   (#3)
```

---

## Pattern 4: Context Recovery

When conversation context compacts, recover state from tasks.

```markdown
### Context Recovery

If context compacts:
1. Call TaskList to see all tasks and their status
2. Read the plan file again
3. Find next pending unblocked task
4. Continue implementation
```

The Task system is **persistent within the session** — even if the conversation summary loses details, `TaskList` retains the full state.

---

## Pattern 5: Exit Criteria Task

Create a final verification task blocked by all implementation tasks.

```json
// After creating all implementation tasks (1-4):
TaskCreate({
  "subject": "Run exit criteria",
  "description": "Run verification script: npm test && npm run lint && npm run typecheck",
  "activeForm": "Running exit criteria"
})
TaskUpdate({
  "taskId": "5",
  "addBlockedBy": ["1", "2", "3", "4"]
})
```

This ensures verification only runs after all work completes.

---

## Visual Progress

Users see task progress via `ctrl+t`:

```
Tasks (2 done, 2 in progress, 3 open)
✓ #1 Setup database schema
■ #2 Implement auth middleware (Worker-1)
■ #3 Add login route (Worker-2)
□ #4 Add protected routes > blocked by #2
□ #5 Run exit criteria > blocked by #2, #3, #4
```

Legend:

- `✓` = completed
- `■` = in_progress
- `□` = pending

---

## Calculating Optimal Parallelism

For swarms, calculate worker count from the task graph:

```markdown
1. Build dependency graph from blockedBy arrays
2. Find maximum width (most concurrent unblocked tasks at any point)
3. Worker count = min(max_width, 10)  # Cap to avoid overload

Example:
#1 ──→ #3 ──→ #5
#2 ──→ #4 ──┘

Max width = 2 (tasks #1 and #2 can run together)
→ Spawn 2 workers
```

If graph is fully linear (A→B→C→D), max width = 1, so swarm degrades to loop behavior.

---

## Anti-Patterns

### Don't create tasks without descriptions

```json
// BAD: Another agent can't understand this
TaskCreate({
  "subject": "Fix the thing"
})

// GOOD: Self-contained description
TaskCreate({
  "subject": "Fix null pointer in user lookup",
  "description": "In src/services/user.ts:42, add null check before accessing user.profile..."
})
```

### Don't forget to set dependencies

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

```markdown
ONLY mark a task as completed when you have FULLY accomplished it.

If you encounter errors, blockers, or cannot finish:
- Keep the task as in_progress
- Create a new task describing what needs to be resolved

Never mark a task as completed if:
- Tests are failing
- Implementation is partial
- You encountered unresolved errors
```

### Don't create circular dependencies

```json
// BAD: Deadlock — neither can start
TaskUpdate({ "taskId": "1", "addBlockedBy": ["2"] })
TaskUpdate({ "taskId": "2", "addBlockedBy": ["1"] })
```

---

## Complete Example: Swarm Worker

From essentials-claude-code `/tasks-swarm`:

```json
Task({
  "description": "Worker-1 executor",
  "subagent_type": "general-purpose",
  "model": "sonnet",
  "run_in_background": true,
  "prompt": "You are Worker-1 in a parallel swarm.

PRD_PATH: ./prd.json

LOOP:
1. TaskList - find all tasks
2. Filter: pending, no owner, blockedBy all completed
3. TaskUpdate - claim: owner: Worker-1, status: in_progress
4. Execute task per description
5. TaskUpdate - status: completed
6. Update prd.json: mark story as passes: true
7. GOTO 1

STOP WHEN: All tasks completed OR no claimable tasks remain
CONFLICT: If already claimed by another, skip and find next"
})
```

**Key elements:**

- Background execution (`run_in_background: true`)
- Self-terminating loop (stops when no work remains)
- Conflict handling (skip if claimed by another worker)
- External state sync (updates prd.json alongside Task system)

---

## When to Use Task Tools

| Scenario | Use Tasks? |
|----------|------------|
| Single simple change | No — just do it |
| Multi-step implementation | Yes — track progress |
| Parallel execution needed | Yes — coordinate workers |
| Long-running work | Yes — survive context compaction |
| User wants visibility | Yes — `ctrl+t` shows progress |

---

## References

- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) — Extracted tool definitions
- [essentials-claude-code](https://github.com/GantisStorm/essentials-claude-code) — Real-world usage examples
- [Claude Code Tasks Are Here (Medium)](https://medium.com/@joe.njenga/claude-code-tasks-are-here-new-update-turns-claude-code-todos-to-tasks-a0be00e70847) — Feature announcement
