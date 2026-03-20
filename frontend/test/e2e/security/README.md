# Security Validation Tests

Comprehensive security testing for the Event Node Builder to verify protection against common web vulnerabilities.

## Test Suite

**File**: `security-validation.spec.ts`

### Tests

1. **test_sql_injection_in_field_alias**
   - Tests SQL injection protection in field alias names
   - Verifies input sanitization and validation
   - Checks HQL output for malicious code

2. **test_sql_injection_in_where_conditions**
   - Tests SQL injection protection in WHERE condition values
   - Verifies parameterization and escaping
   - Ensures generated HQL is safe

3. **test_xss_in_field_display_name**
   - Tests XSS protection in field display names
   - Verifies HTML escaping
   - Ensures scripts don't execute

## Running Tests

```bash
# Run all security tests
cd frontend
npm run test:e2e security-validation.spec.ts

# Run specific test
npm run test:e2e -- -g "test_sql_injection_in_field_alias"

# Run with UI mode
npm run test:e2e:ui -- security-validation.spec.ts
```

## Attack Vectors Tested

### SQL Injection Payloads
- `'; DROP TABLE users; --`
- `1' OR '1'='1`
- `'; DELETE FROM games; --`
- `' OR 1=1--`
- `'; EXEC xp_cmdshell('dir'); --`
- `admin'--`
- `' UNION SELECT * FROM passwords--`

### XSS Payloads
- `<script>alert('XSS')</script>`
- `<img src=x onerror=alert('XSS')>`
- `<svg onload=alert('XSS')>`
- `javascript:alert('XSS')`
- `<iframe src='javascript:alert(XSS)'>`

## Security Measures Verified

### Backend Protection
- ✅ Pydantic schema validation
- ✅ SQLValidator for dynamic identifiers
- ✅ Input sanitization (html.escape)
- ✅ Parameterized queries
- ✅ SQL keyword detection

### Frontend Protection
- ✅ HTML output encoding
- ✅ React's automatic XSS protection
- ✅ Input validation
- ✅ Content Security Policy (if configured)

## Expected Behavior

### SQL Injection Tests
- Input should be rejected or sanitized
- Error message should indicate validation failure
- HQL output should not contain malicious SQL
- No SQL errors should occur

### XSS Tests
- Scripts should not execute
- HTML tags should be escaped
- Display should show plain text or HTML entities
- No injected DOM elements

## Security Best Practices

### Input Validation
```python
# Backend (Pydantic)
from pydantic import BaseModel, Field
import html

class FieldInput(BaseModel):
    alias: str = Field(..., min_length=1, max_length=50)

    @field_validator('alias')
    @classmethod
    def sanitize_alias(cls, v: str) -> str:
        return html.escape(v.strip())
```

### SQL Injection Prevention
```python
# Use SQLValidator for dynamic identifiers
from backend.core.security.sql_validator import SQLValidator

table_name = SQLValidator.validate_table_name(user_input)
column_name = SQLValidator.validate_column_name(user_input)
```

### XSS Prevention
```javascript
// Frontend (React)
// React automatically escapes JSX content
<div>{userInput}</div> // ✅ Safe

// Use DOMPurify for HTML content
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
```

## Related Documentation

- **CLAUDE.md** - Project security rules
- **docs/lessons-learned/security-essentials.md** - Security best practices
- **backend/core/security/sql_validator.py** - SQL injection prevention
- **docs/development/sql-validator-guidelines.md** - SQLValidator usage

## Security Checklist

Before deploying to production, ensure:

- [ ] All security tests pass
- [ ] No console errors related to security
- [ ] No unhandled exceptions during tests
- [ ] Input validation is enabled on all endpoints
- [ ] Output encoding is enabled on all displays
- [ ] SQL injection protection is verified
- [ ] XSS protection is verified
- [ ] Content Security Policy is configured (if applicable)

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** create a public issue
2. **Do not** commit the fix to a public branch
3. **Do** report it privately to the maintainers
4. **Do** include steps to reproduce
5. **Do** suggest a fix if possible

## Maintenance

- Review attack vectors quarterly
- Update payloads based on OWASP Top 10
- Add new tests for discovered vulnerabilities
- Keep dependencies updated

## References

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP XSS](https://owasp.org/www-community/attacks/xss/)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-79: XSS](https://cwe.mitre.org/data/definitions/79.html)
