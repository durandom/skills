# Workflow: Review PARA Structure

Audit the PARA structure for stale, misplaced, or forgotten items.

## Steps

1. **Scan PARA folders**

   ```bash
   # Overview of PARA structure
   echo "=== Projects ===" && ls -la "1_Projects/" 2>/dev/null
   echo "=== Areas ===" && ls -la "2_Areas/" 2>/dev/null
   echo "=== Resources ===" && ls -la "3_Resources/" 2>/dev/null
   echo "=== Archive ===" && ls -la "4_Archive/" 2>/dev/null
   ```

2. **Check for staleness**

   For each category, identify items that may need attention:

   | Category | Staleness Signal |
   |----------|------------------|
   | Projects | No updates in 2+ weeks, or past deadline |
   | Areas | No review in 1+ month |
   | Resources | Never referenced, or outdated info |
   | Archive | (Usually fine, but check for duplicates) |

3. **Present findings**

   Format:

   ```
   ## PARA Review

   ### Projects ([count] active)
   - **Active:** Project-A (last updated: date)
   - **Stale:** Project-B (no updates in 3 weeks) - archive or reactivate?

   ### Areas ([count])
   - Area-1 (healthy)
   - Area-2 (no review in 2 months) - still relevant?

   ### Resources ([count])
   - Topic-1 (referenced recently)
   - Topic-2 (created 6 months ago, never used) - delete?

   ### Archive ([count] items)
   - [count] projects, [count] areas, [count] resources
   ```

4. **Recommend actions**

   For each issue found:
   - Stale project → Archive or add next action
   - Unused resource → Delete or keep with justification
   - Missing index → Create `_INDEX.md`

## Review Cadence

| Review Type | Frequency | Focus |
|-------------|-----------|-------|
| Quick scan | Weekly | Projects status, inbox zero |
| Full review | Monthly | All categories, archiving |
| Deep clean | Quarterly | Resources audit, structure review |
