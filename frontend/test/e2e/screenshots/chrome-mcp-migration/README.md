# Chrome MCP Migration Test Screenshots

This directory contains screenshots from the Chrome MCP Hook Migration E2E test suite.

## Test Coverage

- **8 components** tested
- **32 tests** total (4 tests per component)
- **Screenshots**: 32+ images with timestamps

## Screenshot Naming Convention

```
{component-name}-{action}-{timestamp}.png
```

**Examples**:
- `common-params-modal-open-2026-03-14T15-30-45-123Z.png`
- `category-modal-filled-2026-03-14T15-31-20-456Z.png`
- `game-management-modal-after-search-2026-03-14T15-32-10-789Z.png`

## Screenshot Actions

1. **open** - Modal/form opened successfully
2. **filled** - Chrome MCP fill operations completed
3. **after-save** / **after-submit** / **after-search** - Action completed
4. **error** - Test failure screenshot (if applicable)

## Components Tested

### P0 - Critical Components
- `common-params-modal-*` - CommonParamsModal (4 screenshots)
- `category-modal-*` - CategoryModal (4 screenshots)
- `game-management-modal-*` - GameManagementModal (4 screenshots)

### P1 - High Priority Components
- `event-form-*` - EventForm (4 screenshots)
- `category-form-*` - CategoryForm (4 screenshots)
- `log-form-*` - LogForm (4 screenshots)

### P2 - Medium Priority Components
- `game-form-*` - GameForm (4 screenshots)
- `field-config-modal-*` - FieldConfigModal (4 screenshots)

## Cleanup

Screenshots are **not auto-deleted** after test runs. To clean up:

```bash
# Remove all screenshots
rm -rf frontend/test/e2e/screenshots/chrome-mcp-migration/*.png

# Or remove only error screenshots
rm frontend/test/e2e/screenshots/chrome-mcp-migration/*error*.png
```

## Storage Considerations

- **Typical size**: 50-100 MB for 32 screenshots
- **Format**: PNG (full page screenshots)
- **Retention**: Manual cleanup recommended

## Related Documentation

- Test file: `frontend/test/e2e/chrome-mcp-migration-components.spec.ts`
- Documentation: `docs/development/chrome-mcp-e2e-test-extension.md`
- Migration plan: `docs/development/chrome-mcp-hook-migration-plan.md`
