# Workflow: Guide Decision

<objective>
Help users make categorization and approach decisions within the b4brain system. Walk through decision trees and provide clear recommendations based on the specific situation.
</objective>

<required_reading>
**Read these reference files NOW:**

1. references/decision-trees.md (primary)
2. references/para-method.md (for PARA categorization)
3. references/gtd-workflow.md (for GTD decisions)
</required_reading>

<process>
## Step 1: Understand What's Being Decided

Common decision types:

- **PARA categorization:** "Where should X go?"
- **Context assignment:** "What context should this task have?"
- **Priority assignment:** "How urgent is this?"
- **Actionable vs not:** "Is this something I need to act on?"
- **Command selection:** "What command should I use?"
- **Note type:** "Should this be an atomic note?"

Ask for clarification if the item/situation is unclear.

## Step 2: Gather Context

Ask clarifying questions:

- What is the specific item?
- What's the current situation?
- What outcome are they hoping for?
- Are there constraints or preferences?

## Step 3: Walk Through Relevant Decision Tree

Use the decision trees from `references/decision-trees.md`:

**For PARA categorization:**
Use the `para_categorization` tree
Key questions:

- Is there active work with a deadline?
- Is this an ongoing responsibility?
- Is this reference material?
- Is this inactive but worth keeping?

**For context assignment:**
Use the `context_assignment` tree
Key questions:

- Where/how will this task be done?
- What resources are needed?

**For priority:**
Use the `priority_assignment` tree
Key questions:

- Is there a hard deadline?
- What happens if it's missed?
- Is it important for goals?

## Step 4: Provide Clear Recommendation

Format your recommendation:

```
Based on [key factors]:

**Recommendation:** [Clear decision]

**Reasoning:**
- [Factor 1]
- [Factor 2]

**Implementation:**
[Specific next step or command]
```

## Step 5: Address Edge Cases

If the decision is genuinely ambiguous:

- Acknowledge the ambiguity
- Explain the trade-offs of each option
- Suggest "start with X, move to Y if needed"
- Offer the "when in doubt" default

## Step 6: Confirm Understanding

End with:

- Summary of the decision
- Next action to take
- Offer to help with follow-up questions
</process>

<decision_guidance>

## Quick Decision Heuristics

**When in doubt about PARA category:**
→ Start with Resources (lowest commitment)
→ Promote to Projects/Areas when needed

**When in doubt about actionability:**
→ If you can imagine doing something about it → Actionable
→ If it's purely informational → Reference

**When in doubt about priority:**
→ Default to ⚠️ Medium
→ 🔥 High should be rare and meaningful

**When in doubt about context:**
→ @computer is most common for knowledge work
→ @anywhere for things that don't need specific resources

**When in doubt about atomic notes:**
→ If you can explain it in one sentence → Atomic enough
→ If you need multiple paragraphs → Split it
</decision_guidance>

<common_decisions>

## Common Decision Scenarios

**"I have an article about a technology we're not using yet"**
→ Reference (Resources) unless:

- You're evaluating it for a project → Project folder
- It's part of your tech radar responsibility → Areas

**"My manager asked me to look into something"**
→ Actionable
→ Single step? → Task in _GTD_TASKS.md
→ Multi-step? → Project
→ Define "done" clearly

**"I have meeting notes from a team discussion"**
→ Extract action items → Tasks
→ Remaining content:

- Related to active project → Project folder
- Ongoing team responsibility → Areas
- General reference → Resources

**"I found a cool tool but don't know if I'll use it"**
→ Capture reference in Resources
→ OR add to Someday/Maybe if you want to try it later
→ Delete if it's really just curiosity satisfied

**"This task has been sitting undone for weeks"**
→ Is it still relevant?

- No → Delete it
- Yes but not urgent → Someday/Maybe
- Yes and important → Why isn't it getting done?
  - Wrong context? → Reassign
  - Too vague? → Clarify next action
  - Blocked? → Move to @waiting
  - Overwhelmed? → Break it smaller
</common_decisions>

<success_criteria>
This workflow is complete when:

- [ ] Item/situation understood
- [ ] Relevant decision tree applied
- [ ] Clear recommendation provided
- [ ] Reasoning explained
- [ ] Next action specified
- [ ] User confirms understanding
</success_criteria>
