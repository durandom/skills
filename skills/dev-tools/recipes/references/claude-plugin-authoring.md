# Recipe: Claude Code Plugin Authoring

**Target Audience:** AI Coding Agents and developers packaging skills as installable plugins
**Goal:** Create properly structured `.claude-plugin/` directories so skills can be distributed via the Claude Code marketplace.

> **Source:** Synthesized from production plugin configurations across `durandom/skills`, `durandom/layton`, `durandom/taches-cc-resources-durandom`, and `redhat-developer/rhdh-skill`.

---

## What a Plugin Is

A plugin is a **distribution wrapper** around skills, commands, and agents. It adds two metadata files to your repo so `claude plugin marketplace add` and `claude plugin install` work. The actual skills remain unchanged.

```
your-repo/
├── .claude-plugin/
│   ├── marketplace.json    # Package registry entry
│   └── plugin.json         # Plugin metadata
├── skills/                 # Your skills (unchanged)
├── commands/               # Your commands (unchanged)
└── agents/                 # Your agents (unchanged)
```

---

## marketplace.json

The package registry entry. Defines the package name, owner, and which plugins it contains.

```json
{
  "name": "my-plugin",
  "owner": {
    "name": "your-name"
  },
  "metadata": {
    "description": "What this plugin collection does",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./",
      "description": "Detailed description of what's included",
      "version": "1.0.0",
      "strict": false
    }
  ]
}
```

### Field Reference

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Package name. Becomes the install identifier and skill namespace prefix (`name:skill-name`) |
| `owner.name` | Yes | Author or org name |
| `metadata.description` | Yes | Short description for marketplace listing |
| `metadata.version` | Yes | Semver string |
| `plugins[].name` | Yes | Plugin name. When same as package name, install simplifies to `claude plugin install <name>` |
| `plugins[].source` | Yes | Relative path to plugin root. Always `"./"` for single-plugin repos |
| `plugins[].description` | Yes | Detailed description |
| `plugins[].version` | Yes | Plugin version (usually matches metadata version) |
| `plugins[].strict` | No | `true` = fail if dependencies can't resolve. `false` = lenient. Default: `false` |

### Multiple Plugins in One Package

The `plugins` array can hold multiple entries if you want users to install subsets:

```json
"plugins": [
  { "name": "core", "source": "./", "skills": ["./skills/core"] },
  { "name": "extras", "source": "./", "skills": ["./skills/extras"] }
]
```

Install syntax: `claude plugin install package-name@plugin-name`.

**Recommendation:** Prefer a single plugin per package. Users rarely want partial installs, and it keeps naming simple.

---

## plugin.json

Standalone metadata for the plugin. Contains author info, homepage, and discovery keywords.

```json
{
  "name": "my-plugin",
  "description": "What this plugin does",
  "version": "1.0.0",
  "author": {
    "name": "your-name"
  },
  "homepage": "https://github.com/you/repo",
  "repository": "https://github.com/you/repo",
  "license": "MIT",
  "keywords": [
    "relevant",
    "search",
    "terms"
  ]
}
```

**Keep `name` and `version` consistent** between marketplace.json and plugin.json.

---

## Naming Strategy

The plugin `name` becomes the **namespace prefix** for all skills and commands. Choose wisely:

| Name | Prefix Result | Verdict |
|------|--------------|---------|
| `durandom-skills` | `durandom-skills:commit` | Too long |
| `ds` | `ds:commit` | Good |
| `tcrd` | `tcrd:create-plan` | Good |
| `rhdh` | `rhdh:onboard-plugin` | Good |
| `layton` | `layton:doctor` | Good |

**Rules:**

- Short (2-5 chars) for frequently-typed prefixes
- Meaningful enough to recognize in a skill list
- Lowercase, no special characters

---

## strict: true vs false

| Setting | Use When | Effect |
|---------|----------|--------|
| `strict: true` | All skills are pure markdown, no external CLI deps | Plugin install fails if any dependency can't resolve |
| `strict: false` | Skills depend on external tools (`uv`, `crwl`, `gh`, etc.) | Plugin installs even if some tools are missing |

**Default to `false`** unless you're certain all skills are self-contained.

---

## Installation Commands

### For Users (in README)

```bash
# Register the package source
claude plugin marketplace add owner/repo

# Install the plugin
claude plugin install my-plugin
```

### Scope

| Flag | Effect |
|------|--------|
| `--scope project` | Installs to `.claude/plugins/` in current project only |
| `--scope user` | Installs globally to `~/.claude/plugins/` |
| (no flag) | Default scope (usually project) |

---

## Real-World Examples

### Minimal (single skill, pure markdown)

```json
// marketplace.json — rhdh-skill
{
  "name": "rhdh",
  "owner": { "name": "RHDH Store Manager" },
  "metadata": {
    "description": "Orchestrator skill for RHDH plugin development",
    "version": "0.0.1"
  },
  "plugins": [{
    "name": "rhdh",
    "source": "./",
    "description": "Skills and commands for RHDH plugin lifecycle management",
    "version": "0.0.1",
    "strict": true
  }]
}
```

### Full collection (many skills, external deps)

```json
// marketplace.json — durandom-skills
{
  "name": "ds",
  "owner": { "name": "durandom" },
  "metadata": {
    "description": "Claude Code skills collection",
    "version": "1.0.0"
  },
  "plugins": [{
    "name": "ds",
    "source": "./",
    "description": "Skills, commands, agents, and recipes for Claude Code",
    "version": "1.0.0",
    "strict": false
  }]
}
```

---

## Script Path Portability

When plugins are installed, files are copied to a cache directory. **Never hardcode paths.**

```bash
# BAD — breaks when installed as plugin
./skills/my-skill/scripts/tool.py

# GOOD — resolves at runtime
${CLAUDE_PLUGIN_ROOT}/scripts/tool.py
```

See the [agent-skills recipe](agent-skills.md) for full details on `${CLAUDE_PLUGIN_ROOT}`.

---

## Checklist

```
[ ] .claude-plugin/ directory created
[ ] marketplace.json has name, owner, metadata, plugins array
[ ] plugin.json has name, description, version, author, homepage
[ ] name and version match between both files
[ ] Plugin name is short (will be used as skill prefix)
[ ] strict is set appropriately (true for pure markdown, false otherwise)
[ ] README has installation instructions
[ ] Tested with: claude plugin marketplace add <owner>/<repo>
[ ] Tested with: claude plugin install <name>
```

---

## References

- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference) — Official docs
- [agent-skills.md](agent-skills.md) — Skill authoring patterns (complementary recipe)
