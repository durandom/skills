# Code Review Checklist

Apply these standards when reviewing PRs. Also check for project-specific coding standards (e.g., `CONTRIBUTING.md`, `CODE_QUALITY.md`, or similar) and follow established patterns in the codebase.

## Security

- [ ] No hardcoded credentials or secrets
- [ ] No API keys or tokens in code
- [ ] Input validation for user-provided data
- [ ] No injection vulnerabilities (command, SQL, etc.)

## Architecture

- [ ] Follows existing patterns in similar files
- [ ] No circular dependencies introduced
- [ ] Maintains package/module boundaries
- [ ] No over-engineering or unnecessary complexity

## Code Quality

- [ ] No obvious logic errors
- [ ] Error handling is appropriate (not over-defensive)
- [ ] Code is readable and self-documenting
- [ ] Comments explain "why" not "what"

## Testing

- [ ] Tests included for new functionality
- [ ] Tests cover happy path and error cases
- [ ] Tests actually verify behavior (not just syntax)

## Review Decision Guide

### Approve if

- All critical items pass
- Tests exist and pass
- No security issues
- Minor issues can be addressed in follow-up

### Request Changes if

- Missing tests for new functionality
- Security concerns
- Logic errors
- Violates project conventions

### Close & Refine if

- Implementation fundamentally wrong
- Doesn't match acceptance criteria
- Would require complete rewrite
