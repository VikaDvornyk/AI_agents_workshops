# Python Coding Standards

## Naming Conventions
- Variables and functions: snake_case (e.g., `get_user_name`, `total_count`)
- Classes: PascalCase (e.g., `TaskManager`, `UserProfile`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- Private methods/attributes: prefix with underscore (e.g., `_validate_input`)
- Avoid single-letter variables except in loops (`i`, `j`) or lambdas (`x`)

## Function Design
- Functions should do ONE thing — if the name has "and", split it
- Maximum function length: 20 lines (excluding docstrings)
- Maximum 4 parameters — use dataclass or dict for more
- Always include type hints for parameters and return values
- Every public function must have a docstring

## Error Handling
- Never use bare `except:` — always catch specific exceptions
- Use custom exceptions for domain-specific errors
- Don't silence errors — at minimum, log them
- Validate inputs at system boundaries (user input, API responses)
- Internal function calls can trust their callers — don't over-validate

## Imports
- Group imports: stdlib → third-party → local, separated by blank lines
- Never use `from module import *`
- Prefer absolute imports over relative imports

## Code Organization
- One class per file for large classes
- Keep related functions together
- Constants at the top of the file, after imports
- Main execution code under `if __name__ == "__main__":`

## Comments
- Don't comment WHAT the code does — the code should be self-explanatory
- Comment WHY — explain non-obvious decisions
- Use docstrings for public APIs, not inline comments
- Remove commented-out code — use git history instead
