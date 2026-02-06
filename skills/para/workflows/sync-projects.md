# Workflow: Sync Projects with GTD

Ensure PARA project folders stay in sync with GTD milestones.

## Steps

1. **Get current state**

   Run both commands to see the current state:

   ```bash
   # List PARA project folders
   ls -1 "1_Projects/" 2>/dev/null | grep -v "^_" || echo "No PARA projects folder"

   # List GTD projects (milestones)
   ./.claude/skills/gtd/scripts/gtd project list
   ```

2. **Identify mismatches**

   Compare the two lists:
   - **PARA-only:** Folders in `1_Projects/` with no matching GTD milestone
   - **GTD-only:** GTD milestones with no matching PARA folder
   - **Synced:** Items present in both

3. **Present findings**

   Format:

   ```
   ## Sync Status

   **Synced:** [count]
   - Project-A
   - Project-B

   **PARA-only (no GTD milestone):** [count]
   - Old-Project (consider: archive or create GTD milestone?)

   **GTD-only (no PARA folder):** [count]
   - New-Project (consider: create PARA folder?)
   ```

4. **Offer fixes**

   For each mismatch, offer appropriate action:

   | Mismatch | Options |
   |----------|---------|
   | PARA-only | 1) Create GTD milestone, 2) Archive PARA folder |
   | GTD-only | Create PARA folder with `_INDEX.md` |

5. **Execute chosen fixes**

   - Creating PARA folder:

     ```bash
     mkdir -p "1_Projects/Project-Name"
     # Create _INDEX.md with project overview
     ```

   - Creating GTD milestone:

     ```bash
     ./.claude/skills/gtd/scripts/gtd project create "Project-Name"
     ```

   - Archiving PARA folder:

     ```bash
     mv "1_Projects/Project-Name" "4_Archive/projects/"
     ```

## Naming Convention

Project names should:

- Use kebab-case or Title-Case (be consistent)
- Match exactly between PARA and GTD
- Be descriptive but concise

**Examples:**

- `API-Redesign-v2`
- `Q4-Security-Audit`
- `Team-Onboarding-2024`
