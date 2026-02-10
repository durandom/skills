# Workflow: Guide Decision (GTD vs PARA)

<objective>
Help users decide which system (GTD or PARA) to use for a specific task or item. Direct them to the appropriate standalone skill for execution.
</objective>

<required_reading>
**Read these reference files:**

1. references/unified-workflow.md (for understanding the two-layer model)
</required_reading>

<process>

## Step 1: Understand What the User Has

Ask clarifying questions:

- What is the specific item or task?
- Is it actionable (something to do) or informational (something to organize)?
- What outcome are they hoping for?

## Step 2: Apply the Two-Layer Model

| Question | If Yes | If No |
|----------|--------|-------|
| Is this something to **do** (task, action, project)? | GTD skill | ↓ |
| Is this something to **organize** (file, note, reference)? | PARA skill | ↓ |
| Does it involve **both** systems? | b4brain sync workflow | Ask more questions |

## Step 3: Common Decision Scenarios

**"I need to capture something quickly"**
→ **GTD** - Use `gtd capture "..."` for quick capture

**"Where should I put this article/note?"**
→ **PARA** - Use the `para` skill for categorization help

**"I have a new project to track"**
→ **Both** - Create GTD milestone AND PARA folder (or use b4brain sync)

**"I need to review my tasks"**
→ **GTD** - Use `gtd daily` or `gtd weekly`

**"I need to reorganize my files"**
→ **PARA** - Use the `para` skill

**"My projects are out of sync"**
→ **b4brain** - Use the sync-para-gtd workflow

## Step 4: Provide Clear Recommendation

Format:

```
For [what you described]:

**Use:** [GTD skill / PARA skill / b4brain sync]

**Reason:** [brief explanation]

**Next step:** [specific command or action]
```

## Step 5: Direct to Appropriate Skill

After determining which system:

- GTD tasks → Tell user to use the `gtd` skill
- PARA organization → Tell user to use the `para` skill
- Cross-system sync → Use the b4brain sync workflow

</process>

<quick_decision_guide>

## Quick Reference

| User Wants To... | Use |
|------------------|-----|
| Capture a task | GTD skill |
| Clarify inbox items | GTD skill |
| Review tasks | GTD skill |
| Categorize a file | PARA skill |
| Create project folder | PARA skill |
| Archive old content | PARA skill |
| Sync projects | b4brain sync workflow |
| Understand integration | b4brain skill |

</quick_decision_guide>

<success_criteria>
This workflow is complete when:

- [ ] User's item/task understood
- [ ] Correct system identified (GTD, PARA, or both)
- [ ] User directed to appropriate skill
- [ ] Clear next action provided
</success_criteria>
