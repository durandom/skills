# 🧠 durandom-skills

> 🚀 A collection of Claude Code skills, agents, commands, and recipes to supercharge your productivity!

---

## ✨ What's Inside?

This repository contains **reusable skills and patterns** for Claude Code that help with:

| Component | Description |
|-----------|-------------|
| 🗺️ **Code Mapping** | Navigate codebases like a pro with hierarchical documentation |
| ✅ **GTD** | Getting Things Done task management via CLI |
| 📂 **PARA** | Organize notes by actionability (Projects/Areas/Resources/Archive) |
| 🐙 **GitHub** | GitHub CLI operations for issues, PRs, reviews, and CI |
| 🕷️ **crawl4ai** | Web crawling and data extraction via `crwl` CLI |
| 📝 **Meeting Notes** | Sync meeting transcripts from Google Calendar + Gemini |
| 📖 **Recipes** | Reusable patterns and guides for AI-assisted development |
| ⚡ **Commands** | Slash commands like `/commit`, `/catchup`, `/research` |

---

## 🗂️ Skills

### 🗺️ Code Mapping

> *"Where is this thing? What does this do?"* — Every developer, ever

Hierarchical documentation with **4 zoom levels**:

| Level | Purpose | Example |
|-------|---------|---------|
| 📋 **L0** | System overview | Architecture, entry points |
| 🏘️ **L1** | Domain modules | `auth/`, `api/`, `core/` |
| 📦 **L2** | Individual modules | Classes, key functions |
| 🔍 **L3** | Source code | The actual code |

**Quick Start:**

```bash
# 🔧 Generate code maps from source
uv run python skills/codebase/code-mapping/scripts/code_map.py generate src/ docs/map/

# ✅ Validate existing maps
uv run python skills/codebase/code-mapping/scripts/code_map.py validate docs/map/
```

📚 [Full Documentation →](skills/codebase/code-mapping/SKILL.md)

---

### ✅ GTD (Getting Things Done)

> 🧘 *"Mind like water"* — David Allen

A CLI-based task management system following the **GTD methodology**:

```
📥 Capture → 🔍 Clarify → 🗂️ Organize → 🔄 Reflect → ▶️ Engage
```

**Features:**

- 🏷️ **12 Fixed Labels** — context, energy, status, horizon
- 🎯 **6 Horizons of Focus** — from actions to life purpose
- 📆 **Review Workflows** — daily, weekly, quarterly, yearly
- 🐙 **GitHub Backend** — issues as your task store

**Quick Start:**

```bash
# 📥 Capture a new task
./skills/knowledge/gtd/scripts/gtd capture "Review PR #42"

# 📋 List tasks by context
./skills/knowledge/gtd/scripts/gtd list --context focus --energy high

# 🌅 Start your daily review
./skills/knowledge/gtd/scripts/gtd daily
```

📚 [Full Documentation →](skills/knowledge/gtd/SKILL.md)

---

### 📂 PARA

> 🗂️ *Organize by actionability, not topic*

The PARA method for organizing notes into four categories based on **when you'll need them**:

| Category | Purpose |
|----------|---------|
| 📁 **Projects** | Active goals with deadlines |
| 🔄 **Areas** | Ongoing responsibilities |
| 📚 **Resources** | Topics of interest |
| 🗄️ **Archive** | Inactive items |

Standalone knowledge organization with CLI for project management, folder structure, and archiving.

📚 [Full Documentation →](skills/knowledge/para/SKILL.md)

---

### 🐙 GitHub

> 🔧 *Unified interface for GitHub operations*

GitHub CLI operations using `gh`:

- 📋 **Issue Triage** — prioritize and label issues
- 🔍 **PR Review** — review workflows and checklists
- 🚀 **CI Monitoring** — check pipeline status
- 🤖 **Copilot Iteration** — track Copilot-assisted workflows

📚 [Full Documentation →](skills/dev-tools/github/SKILL.md)

---

### 🕷️ crawl4ai

> 🌐 *Extract web content as clean markdown*

Web crawling and data extraction using the `crwl` CLI. Handles static sites, JavaScript-rendered SPAs, and structured data extraction.

📚 [Full Documentation →](skills/web/crawl4ai/SKILL.md)

---

### 📝 Meeting Notes

> 🎙️ *Sync and manage meeting transcripts*

Syncs Google Calendar meetings with Gemini transcripts, organizing them into a meetings directory with tag-based categorization.

📚 [Full Documentation →](skills/knowledge/meeting-notes/SKILL.md)

---

## ⚡ Commands

### `/commit` 📝

Smart git commits with emoji conventional format:

```bash
/commit          # 🔄 Stage all, run hooks, commit
/commit staged   # 📋 Only commit staged changes
/commit amend    # ✏️ Fix the last commit
/commit split    # 🔀 Interactive multi-commit
/commit dry-run  # 👀 Preview without committing
```

### `/catchup` 🔄

Session restart orientation:

```bash
/catchup         # 📊 Review recent changes
/catchup HEAD~3  # 🕐 Review specific commit
```

### `/research` 🔬

Parallel research with synthesized output:

```bash
/research "topic"            # 📊 Standard research
/research "topic" --quick    # ⚡ Quick overview
/research "topic" --thorough # 🔍 Deep dive
```

---

## 📖 Recipes

Reusable patterns for better development — now a proper skill with router and categorized references.

| Category | Recipes |
|----------|---------|
| 🤖 **AI Agent Patterns** | Agentic CLI, Extract Deterministic, Semantic Zoom |
| 🛠️ **Development Practices** | Comments, Writing Skills, Claude Tools, Snapshot Testing |
| 📦 **Distribution** | Claude Plugin Authoring |
| 🏗️ **Architecture** | Python Project Architecture, Keyring Credential Storage |

📚 [Full Documentation →](skills/codebase/recipes/SKILL.md)

---

## 🤖 Agents

### 🗺️ Code Map Explorer

Navigate codebases following the hierarchical map structure:

```
📖 README → 🏗️ ARCHITECTURE → 🏘️ Domains → 📦 Modules → 🔍 Code
```

---

## 🛠️ Installation

### As a Claude Code Plugin

```bash
claude plugin marketplace add durandom/skills
claude plugin install ds
```

### From Source (for development)

**Prerequisites:**

- 🐍 Python 3.11+
- 📦 [UV](https://github.com/astral-sh/uv) package manager

```bash
# 📥 Clone the repository
git clone https://github.com/durandom/skills.git
cd skills

# 📦 Install dependencies
uv sync

# ✅ Run tests
uv run pytest
```

---

## 📁 Project Structure

```
skills/
├── 📂 skills/                 # 🧠 Core skills (bucketed for skills.sh discovery)
│   ├── codebase/              # 🗺️ Code understanding & patterns
│   │   ├── code-mapping/      # Hierarchical code navigation
│   │   └── recipes/           # Development patterns and guides
│   ├── dev-tools/             # 🛠️ External developer tool CLIs
│   │   ├── github/            # GitHub CLI operations
│   │   ├── jira/              # Jira issue management
│   │   └── cass/              # Claude Code session search
│   ├── knowledge/             # 📚 Personal knowledge & task mgmt
│   │   ├── gtd/               # GTD task management
│   │   ├── para/              # PARA organization
│   │   └── meeting-notes/     # Meeting transcript sync
│   ├── meta/                  # 🧰 Authoring skills/agents
│   │   └── skill-architect/   # Design & audit skills
│   └── web/                   # 🕷️ Web extraction
│       └── crawl4ai/          # Web crawling
├── 📂 commands/         # ⚡ Slash commands
├── 📂 agents/           # 🤖 Subagents
├── 📂 fixtures/         # 🧪 Test fixtures
└── 📂 tests/            # ✅ Project tests
```

---

## 🧪 Development

```bash
# 🧹 Run linting
uv run ruff check .

# 🔧 Auto-fix issues
uv run ruff check --fix .

# ✅ Run tests with snapshots
uv run pytest

# 📸 Update snapshots
uv run pytest --snapshot-update
```

---

## 🎯 Philosophy

This project follows key principles:

| Principle | Description |
|-----------|-------------|
| 🛡️ **Safe by Default** | AI agents can't skip safety steps |
| 📚 **Documentation First** | Good docs enable good retrieval |
| 🎯 **Simple > Clever** | Prefer maintainable over impressive |
| 🔄 **Agentic Workflows** | Designed for AI collaboration |

---

## 📄 License

MIT © durandom

---

<div align="center">

🌟 **Happy coding!** 🌟

Built with ❤️ for Claude Code

</div>
