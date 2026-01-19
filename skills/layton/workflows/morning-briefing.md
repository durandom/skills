<workflow name="morning-briefing">
<objective>Provide context-aware status update.</objective>

<steps>
1. Get temporal context:
   ```bash
   layton context
   ```
2. Get attention items:
   ```bash
   bd list --label watching --json
   ```
3. Get current focus:
   ```bash
   bd list --label focus --json
   ```
4. Synthesize briefing using persona voice (see `references/persona.md`)
</steps>

<synthesis_rules>
Order of presentation:

1. Current focus (if any) — "You're working on..."
2. Attention items sorted by priority — "Watching N items..."
3. Time-appropriate suggestions — based on `time_of_day`

Context adaptation:

- `morning` + `work_hours: true` → full briefing
- `evening` + `work_hours: false` → brief summary only
- attention count > 5 → suggest triage
</synthesis_rules>

<success_criteria>

- [ ] Briefing adapts to time of day
- [ ] Focus item mentioned first (if exists)
- [ ] Attention items summarized with counts
</success_criteria>
</workflow>
