# Code Review Checklist

## Before Approving a PR

### Correctness
- [ ] Does the code do what it claims to do?
- [ ] Are edge cases handled? (empty input, None, zero, negative numbers)
- [ ] Are there off-by-one errors in loops or calculations?
- [ ] Is division by zero possible?
- [ ] Are return values checked for None/error states?

### Security
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] User input is validated and sanitized
- [ ] SQL queries use parameterized statements, not string concatenation
- [ ] File paths are validated — no path traversal vulnerabilities
- [ ] Sensitive data is not logged

### Testing
- [ ] New code has corresponding tests
- [ ] Tests cover happy path AND error cases
- [ ] Test names clearly describe what they test
- [ ] No test depends on another test's state
- [ ] Mocking is used sparingly — prefer integration tests for critical paths

### Code Quality
- [ ] No code duplication — shared logic is extracted
- [ ] Functions are small and focused (max 20 lines)
- [ ] Variable names are descriptive and consistent
- [ ] No unused imports, variables, or dead code
- [ ] Complex logic has explanatory comments (WHY, not WHAT)

### Architecture
- [ ] Changes follow existing patterns in the codebase
- [ ] No circular dependencies introduced
- [ ] New dependencies are justified and minimal
- [ ] Configuration is externalized, not hardcoded
- [ ] Error messages are helpful for debugging

### Documentation
- [ ] Public functions have docstrings
- [ ] README is updated if behavior changes
- [ ] Breaking changes are clearly documented
- [ ] API changes are backwards-compatible or versioned
