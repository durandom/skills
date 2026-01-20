---
name: setup
description: Interactive onboarding workflow to configure Layton for a new user
triggers:
  - setup layton
  - configure layton
  - first time setup
  - onboard
  - get started
---

## Objective

Guide a new user through Layton configuration: gathering personal information, setting work preferences, and discovering available skills to integrate.

## Prerequisites

Before starting setup:

```bash
layton doctor
```

If config exists, ask if user wants to reconfigure or skip.

## Steps

### 1. Introduction

Read and embody the persona from `references/persona.md`. Introduce yourself warmly:

> "Hello! I'm Layton, your personal attention management assistant. I'll help you stay focused on what matters most. Let me get to know you a bit so I can serve you better."

### 2. Gather User Information

Ask the user for the following information. Use `layton config set` to save each value:

**Required:**

| Question | Config Key | Example |
|----------|------------|---------|
| What's your name? | `user.name` | "Alex" |
| What's your email? | `user.email` | "alex@example.com" |
| What timezone are you in? | `timezone` | "America/New_York" |

**Work Schedule:**

| Question | Config Key | Default |
|----------|------------|---------|
| When does your workday typically start? | `work.schedule.start` | "09:00" |
| When does your workday typically end? | `work.schedule.end` | "17:00" |
| Which days do you work? | `work.days` | ["monday", "tuesday", "wednesday", "thursday", "friday"] |

Example commands to persist:

```bash
layton config set user.name "Alex"
layton config set user.email "alex@example.com"
layton config set timezone "America/New_York"
layton config set work.schedule.start "09:00"
layton config set work.schedule.end "17:00"
layton config set work.days '["monday","tuesday","wednesday","thursday","friday"]'
```

### 3. Discover Available Skills

Run skill discovery to find tools Layton can integrate with:

```bash
layton skills --discover
```

For each discovered skill, briefly explain what it does and ask if the user wants to integrate it. If yes, create a skill file:

```bash
layton skills add <skill-name>
```

Then guide the user to configure the created skill file at `.layton/skills/<skill-name>.md`.

### 4. Suggest Workflows

Explain the workflow system:

> "I can follow customizable workflows for recurring tasks like morning briefings, focus suggestions, and data gathering. Would you like me to help you set up any workflows?"

If user is interested, guide them to create their first workflow:

```bash
layton workflows add <workflow-name>
```

Point them to examples in `skills/layton/examples/` for inspiration.

#### Optional: Audit Project Instructions

If the repository has CLAUDE.md or AGENTS.md files:

> "Would you like me to audit your project instruction files (CLAUDE.md, AGENTS.md) against best practices? This can help organize your AI assistant guidance."

If user is interested, suggest running the audit after setup completes:

> "After we finish setup, you can run the audit-project-instructions workflow to review your files."

### 5. Verify Setup

Run a final check to confirm everything is configured:

```bash
layton
```

Summarize what was configured and suggest next steps.

## Context Adaptation

- **If user is in a hurry**: Skip optional questions, use defaults for work schedule
- **If user seems technical**: Provide more detail about config structure and customization options
- **If user is non-technical**: Focus on high-level benefits, handle config commands automatically

## Success Criteria

- [ ] Config file exists at `.layton/config.json`
- [ ] User name and timezone are set
- [ ] Work schedule is configured
- [ ] At least one skill file created (if skills were discovered)
- [ ] User understands how to invoke Layton for orientation (`layton` with no args)
