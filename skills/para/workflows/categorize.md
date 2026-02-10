# Workflow: Categorize Item

Help the user decide where an item belongs in PARA.

## Steps

1. **Ask what they want to categorize**
   - Get a description of the item (note, file, folder, topic)

2. **Apply decision tree**

   Ask these questions in order:

   ```
   Q1: Is this actively being worked on with a deadline or target completion?
   → YES: Projects
   → NO: Continue to Q2

   Q2: Is this an ongoing responsibility you need to maintain over time?
   → YES: Areas
   → NO: Continue to Q3

   Q3: Is this reference material you might need in the future?
   → YES: Resources
   → NO: Continue to Q4

   Q4: Is this completed/inactive work worth keeping?
   → YES: Archive
   → NO: Consider deleting
   ```

3. **Recommend category with reasoning**

   Format:

   ```
   **Category:** [Projects|Areas|Resources|Archive]
   **Reasoning:** [Why this category fits based on their answers]
   **Suggested path:** [e.g., `1_Projects/Project-Name/` or `2_Areas/area-name.md`]
   ```

## Common Edge Cases

| Scenario | Resolution |
|----------|------------|
| "It's both a project and ongoing" | Project for the specific deliverable, Area for the ongoing responsibility |
| "I'm not sure if I'll need it" | Start in Resources, delete if unused after 3 months |
| "It's a project but no deadline" | If there's a clear end state, it's a Project. If not, might be an Area |
| "Multiple topics" | File by primary use case, not by topic |
