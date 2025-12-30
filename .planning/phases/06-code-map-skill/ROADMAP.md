# Roadmap: code-map Skill

## Milestone

- ✅ **v0.1 POC** - Plans 01-04 (complete)

## Plans

### Plan 01: Skill Scaffold + Format Spec

**Goal**: Create skill structure with format specification reference
**Scope**:

- SKILL.md router skeleton
- references/format-spec.md (complete format documentation)
- Basic intake/routing

### Plan 02: Templates

**Goal**: Create templates for each doc level
**Scope**:

- templates/MAP.md
- templates/L0-architecture.md
- templates/L1-domain.md

### Plan 03: Explore Workflow

**Goal**: Agent can read existing map to explore codebase
**Scope**:

- workflows/explore.md
- Test with manual map creation

### Plan 04: Create Workflow + Validation

**Goal**: Agent can generate map for a codebase
**Scope**:

- workflows/create-map.md
- scripts/validate-map.sh
- Dogfood on fvtt2obsidian repo

## Progress

| Plan | Description | Status |
|------|-------------|--------|
| 01 | Skill scaffold + format spec | Complete |
| 02 | Templates | Complete |
| 03 | Explore workflow | Complete |
| 04 | Create workflow + validation | Complete |

---

## v0.2: L2 Module Docs (Future)

**Goal**: Add module-level documentation for complex domains

### Plan 05: L2 Templates + Workflow

**Scope**:

- templates/L2-module.md (200 line limit)
- Update explore workflow to navigate L1 → L2
- Update create workflow to generate L2 when needed

### Plan 06: L2 Validation

**Scope**:

- Validate L2 links from L1 docs
- Check L2 size limits
- Update CLI output

---

## v0.3: Update Workflow (Future)

**Goal**: Detect and fix stale documentation

### Plan 07: Staleness Detection

**Scope**:

- Compare git history of code vs map
- Flag domains where code changed but map didn't
- Generate update suggestions

### Plan 08: Pre-commit Hook

**Scope**:

- Optional hook for validation
- Fast-fail on broken links
- Suggest running update workflow

---

## v0.4: Multi-Language LSP (Future)

**Goal**: Support TypeScript, Go, Rust codebases

### Plan 09: LSP Abstraction

**Scope**:

- Language-agnostic LSP client interface
- TypeScript support (tsserver)
- Go support (gopls)
- Rust support (rust-analyzer)
