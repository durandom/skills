#!/bin/bash
# Create quarterly milestones for career tracking

set -e

echo "Creating quarterly milestones..."

# Q4 2025 (current/past)
echo "→ Q4-2025..."
gh api repos/durandom/pensieve-rhdh/milestones -X POST \
  -f title="Q4-2025" \
  -f description="Q4 2025 (Oct-Dec)" \
  -f due_on="2025-12-31T23:59:59Z" || echo "  (may already exist)"

# Q1 2026
echo "→ Q1-2026..."
gh api repos/durandom/pensieve-rhdh/milestones -X POST \
  -f title="Q1-2026" \
  -f description="Q1 2026 (Jan-Mar)" \
  -f due_on="2026-03-31T23:59:59Z" || echo "  (may already exist)"

# Q2 2026
echo "→ Q2-2026..."
gh api repos/durandom/pensieve-rhdh/milestones -X POST \
  -f title="Q2-2026" \
  -f description="Q2 2026 (Apr-Jun)" \
  -f due_on="2026-06-30T23:59:59Z" || echo "  (may already exist)"

# Q3 2026
echo "→ Q3-2026..."
gh api repos/durandom/pensieve-rhdh/milestones -X POST \
  -f title="Q3-2026" \
  -f description="Q3 2026 (Jul-Sep)" \
  -f due_on="2026-09-30T23:59:59Z" || echo "  (may already exist)"

# Q4 2026
echo "→ Q4-2026..."
gh api repos/durandom/pensieve-rhdh/milestones -X POST \
  -f title="Q4-2026" \
  -f description="Q4 2026 (Oct-Dec)" \
  -f due_on="2026-12-31T23:59:59Z" || echo "  (may already exist)"

echo "✓ Milestones created successfully!"
echo ""
echo "Created milestones: Q4-2025, Q1-2026, Q2-2026, Q3-2026, Q4-2026"
