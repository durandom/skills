# Workflow: Archive PARA Item

Move completed or inactive items to the Archive.

## Steps

1. **Identify what to archive**

   Ask user what they want to archive:
   - Project (most common)
   - Area (role/responsibility ended)
   - Resource (no longer relevant)

2. **Pre-archive checklist**

   ### For Projects

   Before archiving, verify:
   - [ ] All tasks completed or moved elsewhere
   - [ ] Any learnings captured
   - [ ] GTD milestone closed

   ```bash
   # Check GTD project status
   ./.claude/skills/gtd/scripts/gtd project show "Project-Name"
   ```

   ### For Areas

   Before archiving:
   - [ ] No active projects depend on this
   - [ ] Responsibility officially ended
   - [ ] Handoff documentation created (if applicable)

   ### For Resources

   Before archiving:
   - [ ] Confirmed no longer needed
   - [ ] Not referenced by active projects

3. **Execute archive**

   ```bash
   # Archive project
   PROJECT_NAME="Project-Name"
   mkdir -p "4_Archive/projects"
   mv "1_Projects/$PROJECT_NAME" "4_Archive/projects/"

   # Close GTD milestone
   ./.claude/skills/gtd/scripts/gtd project update "$PROJECT_NAME" --state closed

   # Archive area
   AREA_NAME="area-name"
   mkdir -p "4_Archive/areas"
   mv "2_Areas/$AREA_NAME.md" "4_Archive/areas/"
   # or mv "2_Areas/$AREA_NAME/" "4_Archive/areas/"

   # Archive resource
   TOPIC_NAME="topic-name"
   mkdir -p "4_Archive/resources"
   mv "3_Resources/$TOPIC_NAME" "4_Archive/resources/"
   ```

4. **Add archive note (optional)**

   Append to the archived item's index:

   ```
   ## Archived
   - **Date:** YYYY-MM-DD
   - **Reason:** [Completed / Abandoned / No longer relevant]
   - **Outcome:** [Brief summary of result]
   ```

5. **Confirm**

   ```
   Archived: [item]
   - Moved to: 4_Archive/[category]/
   - GTD milestone: [closed/n/a]

   The item is now in cold storage but remains searchable.
   ```

## Archive Structure

```
4_Archive/
├── _INDEX.md           # Archive overview (optional)
├── projects/           # Completed/abandoned projects
├── areas/              # Ended responsibilities
├── resources/          # Outdated reference material
└── YYYY/               # Optional: time-based subfolder
```

## When NOT to Archive

- **Still referenced:** If active work points to it, keep it accessible
- **Might resume soon:** Use "on hold" status instead
- **Unsure:** Leave it, review next month
