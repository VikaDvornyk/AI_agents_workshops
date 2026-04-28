# Testing Guidelines

## Test Structure
- Use the Arrange-Act-Assert (AAA) pattern:
  1. **Arrange**: set up test data and preconditions
  2. **Act**: call the function being tested
  3. **Assert**: verify the result
- One assertion per test when possible
- Test name format: `test_<what>_<condition>_<expected>` (e.g., `test_get_statistics_no_tasks_returns_zero`)

## What to Test
- Happy path: normal inputs produce expected outputs
- Edge cases: empty input, None, zero, negative, very large values
- Error cases: invalid input raises appropriate exceptions
- Boundary conditions: first/last element, max/min values

## What NOT to Test
- Don't test implementation details — test behavior
- Don't test third-party libraries — they have their own tests
- Don't test simple getters/setters with no logic
- Don't test private methods directly — test through public API

## Test Coverage
- Minimum coverage target: 80% for new code
- Critical business logic: 100% coverage required
- Utility functions: must have tests for all public functions
- Bug fixes: every bug fix must include a regression test

## Test Data
- Use factories or fixtures for complex test data
- Don't share mutable test data between tests
- Use realistic but minimal test data
- Avoid random data in tests — tests must be deterministic

## Integration Tests
- Prefer real database for data layer tests — mocks can hide real bugs
- Use test containers or in-memory databases
- Clean up test data after each test
- Test the full request-response cycle for API endpoints

## Common Mistakes
- Testing that a function "was called" instead of testing the result
- Over-mocking: if you mock everything, you test nothing
- Flaky tests: if a test fails randomly, fix it immediately
- Slow tests: unit tests should run in milliseconds, not seconds
