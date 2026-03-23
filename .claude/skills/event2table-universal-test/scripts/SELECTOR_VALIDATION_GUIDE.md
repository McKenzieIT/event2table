# Selector Validation - Quick Usage Guide

## What is Selector Validation?

Selector validation automatically checks if all CSS selectors used in your test configurations actually exist in the web application. This prevents test failures due to incorrect selectors before you run the actual tests.

## When to Use?

### ✅ Use selector validation when:
- Creating new test configurations
- Modifying existing selectors
- After UI changes in the application
- Before running large test suites
- In CI/CD pipelines as a pre-test step

### ❌ Don't need selector validation when:
- Selectors are already proven to work
- Running quick smoke tests
- Testing in a stable environment

## Basic Workflow

### 1. Create Test Configuration

```json
{
  "test_id": "TEST-001",
  "name": "My Test",
  "assertions": [
    {
      "type": "element_exists",
      "selector": ".my-button"
    }
  ]
}
```

### 2. Run Validator

```bash
cd .claude/skills/event2table-universal-test/scripts
./run_validator.sh
```

### 3. Review Report

```
Selector Validation Report
==========================
Total Selectors:  1
Valid:            1 (100.0%)
Invalid:          0 (0.0%)

✅ All selectors are valid!
```

### 4. Fix Issues (if any)

If the report shows invalid selectors:

```
1. .my-button
   Reason: Element not found
   Used in: TEST-001 (My Test)
   💡 Suggestion: Check if class name has changed
```

**Actions:**
- Check the actual HTML in the browser
- Update the selector in your test config
- Run the validator again

## Common Scenarios

### Scenario 1: New Feature Development

```bash
# 1. Create test config for new feature
cat > config/test_configs/new_feature.json << EOF
{
  "test_id": "FEAT-001",
  "name": "New Feature Test",
  "assertions": [
    {"type": "element_exists", "selector": ".new-feature-button"}
  ]
}
EOF

# 2. Validate selectors
./run_validator.sh

# 3. If valid, run tests
./run_tests.py --test-id FEAT-001
```

### Scenario 2: After UI Refactoring

```bash
# 1. Update all selectors in test configs
# (manual edit or automated)

# 2. Validate all selectors
./run_validator.sh --output after_refactor.txt

# 3. Compare with before report
diff before_refactor.txt after_refactor.txt

# 4. Fix any invalid selectors
# 5. Re-validate
./run_validator.sh
```

### Scenario 3: CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Validate Selectors
  run: |
    cd .claude/skills/event2table-universal-test/scripts
    ./run_validator.sh --url http://localhost:5173

- name: Run Tests
  if: success()
  run: npm run test:e2e
```

## Understanding the Report

### Valid Selector (✅)
```
[5/50] Checking: .submit-button
  ✅ VALID - Found: BUTTON (class=submit-button btn-primary, id=)
```
**Meaning:** Selector works correctly, no action needed.

### Invalid Selector (❌)
```
[10/50] Checking: .old-class-name
  ❌ INVALID - Element not found
```
**Meaning:** Selector doesn't match any element in the page.

**Possible causes:**
1. Class name changed in the code
2. Element is conditionally rendered
3. Selector has a typo
4. Page hasn't fully loaded

### Error (⚠️)
```
[15/50] Checking: ::before
  ❌ INVALID - agent-browser error: Invalid selector
```
**Meaning:** Selector syntax is incorrect or not supported.

## Best Practices

### 1. Use Stable Selectors

```css
/* ❌ Bad: Dynamic classes */
.css-123456789-button

/* ❌ Bad: Pseudo-elements */
.button::before

/* ✅ Good: Semantic classes */
.primary-button
.submit-btn
```

### 2. Add Test-Specific Classes

```jsx
// In your React component
<button className="submit-button test-submit-button">
  Submit
</button>
```

```json
// In test config
{
  "selector": ".test-submit-button"
}
```

### 3. Use Data Attributes

```jsx
<button data-testid="submit-button">
  Submit
</button>
```

```json
{
  "selector": "[data-testid='submit-button']"
}
```

### 4. Avoid Complex Selectors

```css
/* ❌ Too complex */
.container > .wrapper .inner-box:last-child .button

/* ✅ Simple and specific */
[data-testid='submit-button']
```

## Troubleshooting

### Problem: "agent-browser not found"

**Solution:**
```bash
npm install -g @agent-browser/cli
```

### Problem: "Application not running"

**Solution:**
```bash
# Start the dev server
cd frontend
npm run dev
```

### Problem: "Timeout checking selector"

**Possible causes:**
1. Application is slow to load
2. Page is very large
3. Network issues

**Solution:**
```python
# In validate_selectors.py, increase timeout
result = subprocess.run(
    ['agent-browser', 'eval', js_code],
    capture_output=True,
    text=True,
    timeout=20  # Increase from 10 to 20
)
```

### Problem: "False negatives (selector is valid but reported invalid)"

**Possible causes:**
1. Element is dynamically loaded
2. Element is only visible after user interaction
3. Selector requires specific page state

**Solution:**
- Add navigation steps to reach the correct page state
- Use wait conditions before validation
- Test selectors manually in browser console first:
  ```javascript
  document.querySelector('.your-selector')
  ```

## Advanced Usage

### Custom URL
```bash
./run_validator.sh --url http://staging.example.com
```

### Save Report
```bash
./run_validator.sh --output /path/to/report.txt
```

### Verbose Mode
```bash
./run_validator.sh --verbose
```

### Direct Python Call
```bash
python3 validate_selectors.py \
  --url http://localhost:5173 \
  --output report.txt \
  --verbose
```

## Integration with Other Tools

### With Test Runner
```bash
# Validate first
./run_validator.sh

# If valid, run tests
if [ $? -eq 0 ]; then
  ./run_tests.py
fi
```

### With Coverage Analyzer
```bash
# 1. Validate selectors
./run_validator.sh

# 2. Analyze coverage
python3 analyze_coverage.py

# 3. Generate combined report
python3 generate_combined_report.py
```

## Tips and Tricks

### 1. Batch Validation
```bash
# Validate multiple environments
for env in local staging production; do
  ./run_validator.sh --url "https://${env}.example.com"
done
```

### 2. Scheduled Validation
```bash
# Run every hour
crontab -e
0 * * * * cd /path/to/scripts && ./run_validator.sh
```

### 3. Pre-commit Hook
```bash
# .git/hooks/pre-commit
./run_validator.sh
if [ $? -ne 0 ]; then
  echo "Invalid selectors detected. Please fix before committing."
  exit 1
fi
```

## FAQ

**Q: How long does validation take?**
A: Typically 1-2 seconds per selector. For 50 selectors, expect ~1 minute.

**Q: Can I validate selectors across multiple pages?**
A: Currently, the validator tests against a single URL. For multi-page tests, validate each page separately.

**Q: What if my selectors are in a different format?**
A: The tool supports CSS selectors. For XPath, you'll need to convert to CSS or extend the tool.

**Q: Can I ignore certain selectors?**
A: Not currently, but you can add a filter to skip specific test IDs or selector patterns.

**Q: Does this work with single-page applications (SPAs)?**
A: Yes, but ensure the page is fully loaded before validation. The tool waits for the page to load but doesn't handle dynamic content changes.

## Next Steps

1. Run the validator on your existing test configs
2. Fix any invalid selectors
3. Add validator to your pre-commit hooks
4. Integrate with CI/CD pipeline
5. Schedule regular validations

## Resources

- [Full Documentation](./SELECTOR_VALIDATOR_README.md)
- [Test Configuration Guide](../README.md)
- [Agent Browser Documentation](https://github.com/agent-browser/cli)
- [CSS Selector Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)

---

**Last Updated:** 2026-03-20
**Version:** 1.0.0
