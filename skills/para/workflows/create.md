# Workflow: Create PARA Item

Create new folders/files in the PARA structure with proper setup.

## Steps

1. **Determine category and name**

   Ask user:
   - What category? (Projects, Areas, Resources)
   - What name?

   If unsure about category, use `workflows/categorize.md` first.

2. **Create based on category**

   ### Project

   ```bash
   PROJECT_NAME="Project-Name"

   # Create PARA folder
   mkdir -p "1_Projects/$PROJECT_NAME"

   # Create index file
   cat > "1_Projects/$PROJECT_NAME/_INDEX.md" << 'EOF'
   # Project: [Name]

   ## Outcome
   [What does "done" look like?]

   ## Status
   - [ ] Active / On Hold / Blocked

   ## Key Files
   - [List important files in this folder]

   EOF
   ```

   ### Area

   ```bash
   AREA_NAME="area-name"

   # Simple area (single file)
   cat > "2_Areas/$AREA_NAME.md" << 'EOF'
   # Area: [Name]

   ## Responsibility
   [What standard am I maintaining?]

   ## Current Status
   [How is this area doing?]

   ## Related Projects
   - [Active projects born from this area]

   ## Review Notes
   - [Date]: [Notes from last review]
   EOF

   # Or complex area (folder)
   mkdir -p "2_Areas/$AREA_NAME"
   # Create similar _INDEX.md inside
   ```

   ### Resource

   ```bash
   TOPIC_NAME="topic-name"

   mkdir -p "3_Resources/$TOPIC_NAME"

   cat > "3_Resources/$TOPIC_NAME/_INDEX.md" << 'EOF'
   # Resource: [Topic]

   ## Purpose
   [Why am I collecting this?]

   ## Contents
   - [List of files/notes in this folder]

   ## Related
   - [Links to related projects/areas]
   EOF
   ```

3. **Confirm creation**

   Show what was created:

   ```
   Created: [path]
   - _INDEX.md initialized


   Next: Add your first file or note to this folder.
   ```

## Naming Conventions

| Category | Convention | Example |
|----------|------------|---------|
| Projects | Title-Case or kebab-case | `API-Redesign`, `Q4-Audit` |
| Areas | lowercase or kebab-case | `engineering-management.md` |
| Resources | lowercase, topic-based | `kubernetes/`, `interview-prep/` |
