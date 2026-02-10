# Workflow: Troubleshoot Cross-System Issues

<objective>
Diagnose and fix issues that span both GTD and PARA systems. For methodology-specific issues, direct users to the standalone skills.
</objective>

<required_reading>
**Read these reference files:**

1. references/common-mistakes.md (system-level mistakes and recovery)
2. references/unified-workflow.md (for understanding the integration)
</required_reading>

<process>

## Step 1: Determine If This Is a Cross-System Issue

This skill handles issues like:

- Projects out of sync between GTD and PARA
- Confusion about which system to use
- System feels too complex (over-engineering)
- Lost trust in the combined system

**Redirect** methodology-specific issues:

- "My GTD inbox is overwhelming" → Use the `gtd` skill
- "I can't find my PARA files" → Use the `para` skill

## Step 2: Identify the Cross-System Symptom

| Symptom | Likely Problem |
|---------|----------------|
| "Projects are out of sync" | GTD milestones ≠ PARA folders |
| "Don't know which system to use" | Missing decision framework |
| "System is too complex" | Over-engineering, too many tools |
| "Lost trust in the system" | Inconsistent usage, drift |

Ask the user:

- What specifically feels wrong?
- When did it start?
- Which parts are working/not working?

## Step 3: Apply Cross-System Fixes

**Projects Out of Sync:**

```
Immediate: Run sync workflow
1. Use b4brain sync-para-gtd workflow
2. Resolve mismatches one by one
3. Establish naming convention

Ongoing: Run sync check weekly during review
```

**Don't Know Which System to Use:**

```
Immediate: Apply two-layer model
- Is it something to DO? → GTD
- Is it something to ORGANIZE? → PARA
- Need both? → Create in both, keep synced

Ongoing: Use guide-decision workflow when unclear
```

**System Too Complex:**

```
Immediate: Simplify
1. Focus on GTD + PARA core only
2. Skip optional features (Zettelkasten, etc.)
3. Reduce to: capture → clarify → organize → review

Ongoing: "Good enough is good enough"
```

**Lost Trust in System:**

```
Immediate: Start fresh
1. Don't try to fix everything
2. Commit to using system for 2 weeks
3. Daily: capture + quick clarify
4. Weekly: sync check + review

Ongoing: Consistency builds trust
```

## Step 4: Provide Recovery Path

For each issue, provide:

1. **Immediate action** - What to do right now
2. **Ongoing habit** - What prevents recurrence
3. **Which skill to use** - GTD, PARA, or b4brain

## Step 5: Confirm Recovery

End with:

- Clear next action
- Reminder that lapses are normal
- Offer follow-up help

</process>

<quick_fixes>

## Quick Fix Reference

| Cross-System Problem | Fix |
|----------------------|-----|
| Projects out of sync | Run b4brain sync workflow |
| Confusion about which system | Apply two-layer model (DO=GTD, ORGANIZE=PARA) |
| System too complex | Simplify to core GTD+PARA only |
| Lost trust | Start fresh, be consistent for 2 weeks |

</quick_fixes>

<recovery_mantras>

## Recovery Mantras

- "GTD for doing, PARA for organizing"
- "Sync once a week, not every day"
- "Imperfect system > no system"
- "The system serves you, not vice versa"

</recovery_mantras>

<success_criteria>
This workflow is complete when:

- [ ] Determined if issue is cross-system or methodology-specific
- [ ] Redirected methodology issues to standalone skills
- [ ] Diagnosed cross-system root cause
- [ ] Provided immediate fix and ongoing habit
- [ ] User has clear next action
</success_criteria>
