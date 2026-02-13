# Archived Diagnostic Tests

This directory contains diagnostic tests that have been archived due to obsolete dependencies.

## Archived Files (2026-02-06)

### test_canvas_nodes.py
- **Reason**: Depends on `generate_hql_from_graph` function which no longer exists
- **Status**: Function removed during flows module refactoring
- **Action Needed**: Test needs complete rewrite using current API

### test_join_fix.py
- **Reason**: Depends on `generate_hql_from_graph` and `_validate_and_align_fields` functions
- **Status**: Functions removed or moved during refactoring
- **Action Needed**: Update to use current HQL generation API

### test_join_hql.py
- **Reason**: Imports from obsolete `modules.flows`
- **Status**: Module path migrated to `backend.services.flows`
- **Action Needed**: Update imports and test logic

### test_union_all_fix.py
- **Reason**: Depends on `generate_hql_from_graph` and `_validate_and_align_fields`
- **Status**: Functions no longer exposed in module API
- **Action Needed**: Rewrite using current flows API

### test_event_nodes_complete.py
- **Reason**: Depends on Playwright which is not installed
- **Status**: Playwright dependency missing
- **Action Needed**: Install Playwright or rewrite as backend-only test

## Notes

These tests were written for an older version of the codebase and depend on functions/modules that no longer exist or have been significantly refactored.

To restore these tests:
1. Review the current API in `backend/services/flows/`
2. Update test logic to use current functions
3. Update import paths
4. Verify dependencies are installed

## Active Tests

See parent directory for active diagnostic tests.
