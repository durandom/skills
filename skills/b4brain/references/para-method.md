# PARA Method Reference

<overview>
PARA (Projects, Areas, Resources, Archives) is a digital organization system developed by Tiago Forte. It organizes information by **actionability** - how soon you'll need it - rather than by topic. This creates an environment that naturally surfaces what's most relevant to current work.
</overview>

<core_principle>

## The Core Innovation: Actionability Over Topic

Traditional filing organizes by subject (e.g., "JavaScript", "Marketing", "Finance"). PARA organizes by **when and how you'll use the information**:

**Example:** An article about Kubernetes best practices:

- Goes in **Projects** if you're deploying Kubernetes this week
- Goes in **Areas** if you maintain Kubernetes systems as an ongoing responsibility
- Goes in **Resources** if you're just interested in learning
- Goes in **Archives** if you used it for a completed project

This simple shift eliminates the question "Where would I look for this?" because the answer is always "Where am I likely to need it?"
</core_principle>

<four_pillars>

## The Four Categories

<category name="Projects">
**Definition:** A series of tasks linked to a specific goal with a deadline or timeframe.

**Key characteristics:**

- Has a clear, achievable outcome
- Has a defined timeline (even if approximate)
- Can be "completed" and moved to Archive
- Contains all materials needed to make progress

**Examples in b4brain:**

- `1 Projects/API-Redesign-v2/` - Active development initiative
- `1 Projects/Team-Onboarding/` - Specific onboarding program
- `1 Projects/Security-Audit-Q4/` - Time-bound audit

**Signals it's a Project:**

- "Complete", "deliver", "launch", "finish" language
- Specific deadline or milestone
- Can visualize what "done" looks like
</category>

<category name="Areas">
**Definition:** Spheres of responsibility that require a standard to be maintained over time, with no end date.

**Key characteristics:**

- Ongoing, never "complete"
- Represents a role or responsibility
- Has standards or metrics to maintain
- Source of new projects

**Examples in b4brain:**

- `2 Areas/Engineering-Management.md` - Ongoing leadership responsibility
- `2 Areas/Architecture-Reviews.md` - Recurring responsibility
- `2 Areas/Team-Health.md` - Continuous monitoring

**Signals it's an Area:**

- "Maintain", "manage", "oversee", "track" language
- No end date
- Failure means dropping a standard, not missing a deadline

**Project vs Area distinction:**

- You don't "complete" your health - you maintain it (Area)
- You can complete a "Run 5K race" goal (Project born from Area)
</category>

<category name="Resources">
**Definition:** Topics of ongoing interest that are not tied to a project or area of responsibility.

**Key characteristics:**

- No responsibility attached
- Reference material for potential future use
- Organized by topic/interest
- Can feed into projects when needed

**Examples in b4brain:**

- `3 Resources/kubernetes/` - Learning materials and references
- `3 Resources/system-design-patterns/` - Architectural knowledge
- `3 Resources/rhdh-backstage-resources.md` - Product documentation

**Signals it's a Resource:**

- "Interesting", "might need", "good to know" language
- No immediate application
- Would be useful if a related project arose

**Warning:** Resources can become a dumping ground. Without synthesis (via Zettelkasten), collected information remains inert.
</category>

<category name="Archives">
**Definition:** Inactive items from the other three categories.

**Key characteristics:**

- "Cold storage" for completed/paused work
- Preserves context and history
- Searchable when needed
- Not deleted - just out of sight

**Examples in b4brain:**

- `4 Archive/projects/API-Redesign-v1/` - Completed project
- `4 Archive/2023/` - Time-based archival
- Items no longer maintained but potentially useful

**When to archive:**

- Project completed or abandoned
- Area of responsibility ended (changed roles)
- Resource no longer of interest
</category>

</four_pillars>

<just_in_time>

## Just-in-Time Organization

PARA avoids over-organization through "just-in-time" structuring:

**DO:**

- Create folders when you have something to put in them
- Let structure emerge from actual work
- Keep things simple until complexity is needed
- Move items between categories as their status changes

**DON'T:**

- Pre-create elaborate folder hierarchies
- Spend more time organizing than working
- Create empty placeholder folders
- Treat the structure as permanent
</just_in_time>

<b4brain_implementation>

## PARA in b4brain

**Folder naming conventions:**

```
1 Projects/     # Numbered prefix for sort order
2 Areas/
3 Resources/
4 Archive/
```

**Index files:**
Each PARA folder contains `_INDEX.md` for navigation and overview.

**Integration with GTD:**

- PARA provides the filing cabinet
- GTD provides the workflow to populate it
- Items are processed via `/inbox` into PARA folders

**Integration with Zettelkasten:**

- Resources contain the Zettelkasten (`3 Resources/zettelkasten/`)
- Project learnings get synthesized via `/connect`
- Knowledge persists even after projects archive
</b4brain_implementation>

<decision_guidance>

## Categorization Decision Tree

```
Is this actively being worked on with a deadline?
├── YES → Projects
└── NO ↓

Is this an ongoing responsibility I maintain?
├── YES → Areas
└── NO ↓

Is this something I might reference later?
├── YES → Resources
└── NO ↓

Is this something I'm done with but want to keep?
├── YES → Archive
└── NO → Delete it
```

**When in doubt:**

- Start with Resources (lowest commitment)
- Promote to Projects or Areas when needed
- Archive when no longer active
</decision_guidance>
