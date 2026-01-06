# 🧠 durandom-skills

> 🚀 A collection of Claude Code skills, agents, commands, and recipes to supercharge your productivity!

---

## ✨ What's Inside?

This repository contains **reusable skills and patterns** for Claude Code that help with:

| Component | Description |
|-----------|-------------|
| 🗺️ **Code Mapping** | Navigate codebases like a pro with hierarchical documentation |
| ✅ **GTD** | Getting Things Done task management via CLI |
| 🧠 **b4brain** | Personal knowledge management using PARA + GTD |
| ⚡ **Commands** | Slash commands like `/commit` and `/catchup` |
| 📖 **Recipes** | Reusable patterns for AI-safe development |

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
uv run python skills/code-mapping/scripts/code_map.py generate src/ docs/map/

# ✅ Validate existing maps
uv run python skills/code-mapping/scripts/code_map.py validate docs/map/
```

📚 [Full Documentation →](skills/code-mapping/SKILL.md)

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
./skills/gtd/scripts/gtd capture "Review PR #42"

# 📋 List tasks by context
./skills/gtd/scripts/gtd list --context focus --energy high

# 🌅 Start your daily review
./skills/gtd/scripts/gtd daily
```

📚 [Full Documentation →](skills/gtd/SKILL.md)

---

### 🧠 b4brain

> 🗃️ Personal knowledge management expertise

Combines two powerful methodologies:

| Method | Purpose |
|--------|---------|
| 📂 **PARA** | Organize by actionability (Projects/Areas/Resources/Archive) |
| ✅ **GTD** | Externalize mental load, capture everything |

**When to use:**

- 🤔 *"Where should I put this?"* → Ask b4brain
- 🔀 *"Should this be a Project or Area?"* → Ask b4brain
- 🧹 *"My system feels cluttered"* → Troubleshoot with b4brain

📚 [Full Documentation →](skills/b4brain/SKILL.md)

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

---

## 📖 Recipes

Reusable patterns for better development:

| Recipe | Description |
|--------|-------------|
| 🛡️ **Safe-by-Default CLI** | Hide destructive flags, safe defaults for AI agents |
| 📸 **Snapshot Testing** | Testing with syrupy |
| 💬 **Comments** | Python commenting standards for agentic workflows |
| 🔐 **Keyring Storage** | Secure credential management |

---

## 🤖 Agents

### 🗺️ Code Map Explorer

Navigate codebases following the hierarchical map structure:

```
📖 README → 🏗️ ARCHITECTURE → 🏘️ Domains → 📦 Modules → 🔍 Code
```

---

## 🛠️ Installation

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
├── 📂 skills/           # 🧠 Core skills
│   ├── code-mapping/    # 🗺️ Hierarchical code navigation
│   ├── gtd/             # ✅ Task management
│   └── b4brain/         # 🧠 Knowledge management
├── 📂 commands/         # ⚡ Slash commands
├── 📂 agents/           # 🤖 Subagents
├── 📂 recipes/          # 📖 Reusable patterns
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
