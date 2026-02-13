# Test Archive Directory

This directory contains disabled and obsolete test files that have been archived for reference purposes.

## Directory Structure

```
archive/
├── disabled/
│   ├── e2e/           # Disabled E2E Playwright tests
│   └── backend/       # Disabled backend unit tests
└── README.md          # This file
```

## Archived Files

### E2E Tests (5 files)

All files located in `disabled/e2e/`:

1. **tdz-diagnostic.spec.ts.disabled** (2.9K)
   - Diagnostic tests for TDZ (Temporal Dead Zone) issues
   - Disabled due to: Code refactoring that resolved TDZ issues

2. **textbutton-fieldcanvas.spec.ts.disabled** (7.1K)
   - Tests for TextButton component in Field Canvas
   - Disabled due to: Component API changes / replacement with newer implementation

3. **wait-test.spec.ts.disabled** (1.3K)
   - Tests for wait/sleep functionality
   - Disabled due to: Utility function changes or integration improvements

4. **where-builder-debug.spec.ts.disabled** (3.7K)
   - Debug tests for WHERE clause builder
   - Disabled due to: Debug instrumentation removed from production code

5. **where-builder.spec.ts.disabled** (5.8K)
   - Tests for WHERE clause builder functionality
   - Disabled due to: Major refactoring of WHERE builder logic

## Why Files Are Archived

These test files are disabled but kept for the following reasons:

1. **Reference**: They may contain useful test scenarios or edge cases
2. **Documentation**: They document historical behavior and API changes
3. **Reactivation**: They can be reactivated if needed for regression testing
4. **Audit Trail**: They provide a history of what was tested previously

## Archiving Criteria

Files are archived when they meet one or more of these criteria:

- ✅ Marked with `.disabled` extension (explicitly disabled)
- ✅ Testing obsolete features that no longer exist
- ✅ Conflicting with current code architecture
- ✅ superseded by newer test implementations
- ✅ Debug/instrumentation tests no longer relevant

## Reactivation Process

To reactivate an archived test:

1. **Review**: Check if the test is still relevant to current code
2. **Update**: Modify test to match current API/behavior
3. **Rename**: Remove `.disabled` extension
4. **Move**: Move back to active test directory
5. **Verify**: Run test to ensure it passes

## Maintenance

- **Last Updated**: 2026-02-11
- **Archived By**: Automated archiving process
- **Total Files**: 5 E2E tests
- **Total Size**: ~21KB

## Related Documentation

- [Testing Guide](../../docs/development/testing-guide.md)
- [TDD Practices](../../docs/development/tdd-practices.md)
- [E2E Testing Guide](../../E2E_TESTING_GUIDE.md)

---

**Note**: Do NOT delete files from this archive without explicit approval from the development team. These files serve as historical reference and may be needed for future debugging or feature restoration.
