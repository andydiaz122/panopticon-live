```markdown
# panopticon-live Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `panopticon-live` TypeScript codebase. You'll learn about file naming, import/export styles, commit message conventions, and how to write and run tests using Vitest. This guide will help you contribute code that matches the project's established standards.

## Coding Conventions

### File Naming
- **Pattern:** PascalCase
- **Example:**  
  ```plaintext
  MyComponent.ts
  DataProcessor.ts
  ```

### Import Style
- **Pattern:** Use aliases for imports.
- **Example:**
  ```typescript
  import { Logger } from '@utils/Logger';
  ```

### Export Style
- **Pattern:** Mixed (both named and default exports are used).
- **Examples:**
  ```typescript
  // Named export
  export function processEvent(event: Event) { ... }

  // Default export
  export default class DataProcessor { ... }
  ```

### Commit Messages
- **Pattern:** Conventional commits with `feat` prefix.
- **Example:**
  ```
  feat: add real-time event streaming to dashboard
  ```

## Workflows

### Writing Code
**Trigger:** When adding new features or updating existing code  
**Command:** `/write-code`

1. Name new files using PascalCase (e.g., `NewFeature.ts`).
2. Use alias imports for internal modules.
3. Choose between named or default exports as appropriate.
4. Write clear, conventional commit messages prefixed with `feat`.

### Running Tests
**Trigger:** When verifying code changes  
**Command:** `/run-tests`

1. Write tests in files matching the pattern `*.test.ts`.
2. Use Vitest for all test cases.
3. Run the test suite with Vitest to ensure all tests pass.

   **Example test file:**
   ```typescript
   // DataProcessor.test.ts
   import { describe, it, expect } from 'vitest';
   import DataProcessor from '@core/DataProcessor';

   describe('DataProcessor', () => {
     it('should process data correctly', () => {
       const processor = new DataProcessor();
       expect(processor.process([1, 2, 3])).toEqual([2, 3, 4]);
     });
   });
   ```

## Testing Patterns

- **Framework:** Vitest
- **Test file pattern:** `*.test.ts`
- **Example:**
  ```typescript
  // Logger.test.ts
  import { describe, it, expect } from 'vitest';
  import { Logger } from '@utils/Logger';

  describe('Logger', () => {
    it('logs messages', () => {
      const logger = new Logger();
      expect(logger.log('hello')).toBe(true);
    });
  });
  ```

## Commands
| Command      | Purpose                                   |
|--------------|-------------------------------------------|
| /write-code  | Start a new feature or code update        |
| /run-tests   | Run the Vitest test suite                 |
```
