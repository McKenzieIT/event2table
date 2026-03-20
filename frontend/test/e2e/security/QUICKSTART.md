# Security Tests - Quick Start

## Quick Run

```bash
# Navigate to frontend directory
cd /Users/mckenzie/Documents/event2table/frontend

# Run all security tests
npm run test:e2e -- security-validation.spec.ts

# Run with UI mode (recommended for debugging)
npm run test:e2e:ui -- security-validation.spec.ts

# Run with debug mode
npm run test:e2e:debug -- security-validation.spec.ts

# Run specific test
npm run test:e2e -- -g "test_sql_injection_in_field_alias"
npm run test:e2e -- -g "test_sql_injection_in_where_conditions"
npm run test:e2e -- -g "test_xss_in_field_display_name"
```

## Prerequisites

1. **Backend server running**
   ```bash
   cd /Users/mckenzie/Documents/event2table
   source backend/venv/bin/activate
   python web_app.py
   ```

2. **Frontend dev server running**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test data available**
   - Game GID: 10000147 (STAR001)
   - Database initialized with test data

## Understanding Test Results

### ✅ Passing Tests
- All security measures are working
- Input validation is active
- Output encoding is working
- No malicious code in output

### ❌ Failing Tests
- Security vulnerability detected
- Input validation missing
- Output encoding not working
- Malicious code in output

### ⚠️ Warnings
- Test couldn't complete (UI element not found)
- Need to verify manually
- Inconclusive result

## Test Coverage

| Security Area | Tests | Coverage |
|---------------|-------|----------|
| SQL Injection | 2 | Field aliases, WHERE conditions |
| XSS | 1 | Field display names |
| Input Validation | 3 | All inputs |
| Output Encoding | 2 | HQL preview, UI display |

## Attack Vectors

### SQL Injection (7 payloads)
```javascript
"'; DROP TABLE users; --"
"1' OR '1'='1'
"'; DELETE FROM games; --"
"' OR 1=1--"
"'; EXEC xp_cmdshell('dir'); --"
"admin'--"
"' UNION SELECT * FROM passwords--"
```

### XSS (7 payloads)
```javascript
"<script>alert('XSS')</script>"
"<img src=x onerror=alert('XSS')>"
"<svg onload=alert('XSS')>"
"javascript:alert('XSS')"
"<iframe src='javascript:alert(XSS)'>"
"<body onload=alert('XSS')>"
"'><script>alert(String.fromCharCode(88,83,83))</script>"
```

## Console Output

During test execution, you'll see:

```
[Security Test] Testing SQL injection in field alias...
[Security Test] Testing payload: '; DROP TABLE users; --...
[Security Test] Step 1: Opening field configuration modal...
[Security Test] Step 2: Locating alias input field...
[Security Test] Step 3: Inputting SQL injection payload...
[Security Test] Step 4: Attempting to save configuration...
[Security Test] ✓ Save rejected with error: Invalid input
[Security Test] Step 5: Checking HQL preview...
[Security Test] ✓ HQL does not contain malicious SQL code
[Security Test] ✓ Test completed
```

## Screenshots

Failed tests automatically save screenshots to:
```
frontend/test/e2e/security/screenshots/
```

Screenshot naming: `{test_name}.png`

## Troubleshooting

### Issue: Tests fail with "Element not found"
**Solution**: Ensure Event Node Builder page loads correctly
```bash
# Verify page loads
curl http://localhost:5173/#/event-node-builder?game_gid=10000147
```

### Issue: Save button not visible
**Solution**: Check if modal is open and UI is responsive
```bash
# Run with UI mode to see what's happening
npm run test:e2e:ui -- security-validation.spec.ts
```

### Issue: HQL preview not updating
**Solution**: Click HQL preview button manually and check for errors
```bash
# Check console for errors
npm run test:e2e:debug -- security-validation.spec.ts
```

## Security Checklist

After running tests, verify:

- [ ] All 3 tests pass
- [ ] No console errors
- [ ] No malicious code in HQL output
- [ ] No script execution detected
- [ ] All inputs properly validated
- [ ] All outputs properly encoded

## Next Steps

1. **If all tests pass**: Security measures are working ✅
2. **If tests fail**: Review console logs and screenshots
3. **If warnings appear**: Manual verification needed
4. **Report issues**: Create security issue ticket

## Related Files

- Test file: `security-validation.spec.ts`
- Documentation: `README.md`
- Project rules: `../../../../../CLAUDE.md`
- Security guide: `../../../../../../docs/lessons-learned/security-essentials.md`

## Support

For questions or issues:
1. Check the main README.md
2. Review CLAUDE.md security rules
3. Consult docs/lessons-learned/security-essentials.md
