<overview>

# GTD Horizons of Focus - Template

This is a **template** for the HORIZONS.md file that should live at the root of your b4brain vault.

**To use:** Copy this file to your vault root as `HORIZONS.md` and fill in your personal content.

```bash
cp <skill-directory>/references/horizons.md ~/path/to/vault/HORIZONS.md
```

David Allen's GTD methodology defines 6 "Horizons of Focus" - different altitudes at which you view your work and life. Lower horizons are tactical (daily actions), higher horizons are strategic (life purpose).

</overview>

<horizons_summary>

## The 6 Horizons

| Horizon | Name | Review Cadence | Tracked Via |
|---------|------|---------------|-------------|
| Ground | Actions | Daily | `horizon/action` label via gtd CLI |
| H1 | Projects | Weekly | `horizon/project` label via gtd CLI |
| **H2** | Areas of Focus | Quarterly | `2_Areas/` folder (PARA) |
| **H3** | Goals | Quarterly | `horizon/goal` label via gtd CLI |
| **H4** | Vision | Yearly | This document (HORIZONS.md) |
| **H5** | Purpose & Principles | Yearly | This document (HORIZONS.md) |

**Integration with PARA:**

- H2_Areas already exist in your `2_Areas/` folder - don't duplicate them here
- H3 Goals are tracked via gtd CLI so you can link projects and actions to them
- H4/H5 are strategic and rarely change - they live in this file

</horizons_summary>

<horizon_2>

## H2: Areas of Focus & Responsibility

**Location:** `2_Areas/` folder in your b4brain vault

Areas are ongoing responsibilities that require maintenance. Unlike projects (which end), areas persist. In b4brain, these are already organized in the PARA structure.

**Key questions:**

- What do I need to maintain at a consistent standard?
- Where am I accountable?
- What would fall apart if I stopped paying attention?

### Review Questions (Quarterly)

1. Am I neglecting any area in `2_Areas/`?
2. Are my projects balanced across areas?
3. Should I add or remove any areas?
4. Where am I overcommitted?

**Tip:** Run `ls "2_Areas/"` to review your current areas during quarterly review.

</horizon_2>

<horizon_3>

## H3: Goals (1-2 Years)

**Location:** Tracked via gtd CLI with `horizon/goal` label

Goals are specific outcomes you want to achieve. They have clear success criteria and a timeframe. Tracking them via gtd lets you link projects and actions to them.

**Key questions:**

- What do I want to accomplish in the next 1-2 years?
- What would make this year a success?
- What goals support my vision?

### Creating Goals

```bash
./gtd add "Achieve AWS Solutions Architect certification" --horizon goal
./gtd add "Run a half marathon" --horizon goal
./gtd add "Launch sidekick to 100 users" --horizon goal

# List all goals
./gtd list --horizon goal
```

### Good Goals

- Specific outcome (not vague)
- Measurable (know when done)
- Aligned with vision (H4)
- Use `--due` for timeframe, not in the title

### Review Questions (Quarterly)

1. Am I making progress on my goals? (`./gtd list --horizon goal`)
2. Are these still the right goals?
3. What projects support these goals?
4. Any goals to add, modify, or retire?

</horizon_3>

<horizon_4>

## H4: Vision (3-5 Years)

Vision is a picture of success. What does life look like if you're doing everything right?

**Key questions:**

- Where do I want to be in 3-5 years?
- What does success look like?
- What would I regret not doing?

### Template

```markdown
## My 3-5 Year Vision

### Career
In 5 years, I see myself as...
- [Describe your ideal work situation]
- [Key achievements you'll have made]
- [Skills you'll have mastered]

### Personal Life
- [Health and wellness picture]
- [Relationships and family]
- [Lifestyle and location]

### Impact
- [How you're contributing]
- [What you're known for]
- [Legacy you're building]
```

### Review Questions (Yearly)

1. Is this vision still inspiring?
2. Am I moving toward or away from this vision?
3. What needs to change to make this real?
4. What goals for next year align with this vision?

</horizon_4>

<horizon_5>

## H5: Purpose & Principles

Purpose is your "why" - the reason you get up in the morning. Principles are the values that guide your decisions.

**Key questions:**

- Why do I do what I do?
- What do I believe in?
- What would I never compromise on?

### Template

```markdown
## My Purpose

One sentence: I exist to...

## My Principles

1. **[Principle Name]**
   [What it means and why it matters]

2. **[Principle Name]**
   [What it means and why it matters]

3. **[Principle Name]**
   [What it means and why it matters]

## Decision Filter

When faced with a tough choice, I ask:
1. [First question based on principles]
2. [Second question]
3. [Third question]
```

### Review Questions (Yearly)

1. Am I living according to my principles?
2. Does my vision align with my purpose?
3. Any principles I need to add or clarify?
4. Am I proud of how I'm showing up?

</horizon_5>

<review_rhythms>

## Review Rhythms

### Daily (5 min)

- `./gtd daily`
- Focus on Ground level (actions)

### Weekly (15-30 min)

- `./gtd weekly`
- Ground level + H1 (projects)
- Process inbox to zero
- Ensure every project has a next action

### Quarterly (1-2 hours)

- `./gtd quarterly`
- H2 (areas) + H3 (goals)
- Review and update Areas of Focus section above
- Set goals for next quarter
- Capture achievements

### Yearly (2-4 hours)

- `./gtd yearly`
- H4 (vision) + H5 (purpose)
- Review and update Vision and Purpose sections above
- Set yearly goals
- Reflect on principles

</review_rhythms>

<your_horizons>

---

# YOUR HORIZONS

Fill in the sections below during your yearly review.

**Note:** H2_Areas live in `2_Areas/` folder, H3 Goals are GitHub Issues.

---

## H5: Purpose & Principles

**My Purpose:**
[One sentence: I exist to...]

**My Principles:**

1. [Principle 1 - what it means]
2. [Principle 2 - what it means]
3. [Principle 3 - what it means]

**Decision Filter:**
When faced with a tough choice, I ask:

1. [Question based on principles]
2. [Question based on principles]

---

## H4: Vision (3-5 Years)

**Career:**
[What does success look like in 3-5 years?]

**Personal:**
[Health, relationships, lifestyle]

**Impact:**
[How you're contributing, what you're known for]

---

</your_horizons>
