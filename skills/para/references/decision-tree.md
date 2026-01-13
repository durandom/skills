# PARA Categorization Decision Tree

<overview>
This decision tree helps you determine where content belongs in the PARA structure.
</overview>

<para_categorization>

## Where Does This Belong?

```
Start with the item to organize
           │
           ▼
Is there active work on this with a deadline?
├── YES → 1 Projects/
│         • Has clear outcome
│         • Has timeline
│         • Can be "completed"
│
└── NO ──▼

Is this an ongoing responsibility I maintain?
├── YES → 2 Areas/
│         • No end date
│         • Has standards to maintain
│         • Part of a role/responsibility
│
└── NO ──▼

Could this be useful reference material later?
├── YES → 3 Resources/
│         • Topic of interest
│         • No immediate use
│         • Reference value
│
└── NO ──▼

Is this completed/historical but worth keeping?
├── YES → 4 Archive/
│         • Completed project
│         • Past reference
│         • Historical record
│
└── NO → Delete it
```

</para_categorization>

<examples>

## Common Examples

| Item | Category | Why |
|------|----------|-----|
| Article about Kubernetes (deploying now) | 1 Projects/ | Active work with deadline |
| Article about Kubernetes (I maintain K8s) | 2 Areas/ | Ongoing responsibility |
| Article about Kubernetes (just interested) | 3 Resources/ | Reference for later |
| My old project from 2023 | 4 Archive/ | Completed work |
| Random bookmark I'll never use | Delete | No value |

</examples>
