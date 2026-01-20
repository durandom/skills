## default output

```
❯ .claude/skills/layton/scripts/layton
{
  "success": true,
  "data": {
    "checks": [
      {
        "name": "beads_available",
        "status": "pass",
        "message": "bd CLI available at /opt/homebrew/bin/bd"
      },
      {
        "name": "beads_initialized",
        "status": "pass",
        "message": "Beads initialized at /Users/mhild/src/durandom/pensieve-rhdh/.beads"
      },
      {
        "name": "config_exists",
        "status": "pass",
        "message": "Config found at /Users/mhild/src/durandom/pensieve-rhdh/.layton/config.json"
      },
      {
        "name": "config_valid",
        "status": "pass",
        "message": "Config is valid JSON"
      }
    ],
    "skills": [
      {
        "name": "gtd",
        "description": "GTD task management. Query for active tasks, inbox items, projects, and daily context when preparing briefings."
      }
    ],
    "workflows": [
      {
        "name": "morning-briefing",
        "description": "<what this workflow does>",
        "triggers": [
          "<phrase that activates this workflow>",
          "<another trigger phrase>"
        ]
      }
    ]
  },
  "next_steps": []
}
```

-> this should only show checks results, if there are problems

## AGENTS.md / CLAUDE.md

- check integration:
  - CLAUDE.md `@AGENTS.md`
  - not too verbose about bd integration in AGENTS.md
  - maybe we should make sure to always invoke the layton skill in CLAUDE.md?

## Workflows

- After each workflow we should do a short retrospection if the workflow needs adjustments.
