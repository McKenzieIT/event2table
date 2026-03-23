# Selector Validation Tool

## Overview

The Selector Validation Tool automatically validates all CSS selectors used in test configurations by checking if they exist in the actual web application using `agent-browser`.

## Features

- ✅ **Automated Validation**: Checks all selectors from test configurations
- ✅ **Real Browser Testing**: Uses agent-browser for accurate validation
- ✅ **Detailed Reports**: Generates comprehensive validation reports
- ✅ **Fix Suggestions**: Provides suggestions for common selector issues
- ✅ **Multi-Environment Support**: Test against local, staging, or production
- ✅ **Duplicate Detection**: Handles duplicate selectors efficiently

## Installation

### Prerequisites

1. **Python 3.7+**
   ```bash
   python3 --version
   ```

2. **agent-browser**
   ```bash
   npm install -g @agent-browser/cli
   ```

3. **Event2Table Application Running**
   - For local testing: Start the dev server (`npm run dev`)
   - For production: Ensure the application is accessible

## Usage

### Quick Start (Local Development)

```bash
cd .claude/skills/event2table-universal-test/scripts
./run_validator.sh
```

### Advanced Usage

```bash
# Test against custom URL
./run_validator.sh --url http://localhost:3000

# Test against staging
./run_validator.sh --staging

# Test against production
./run_validator.sh --production

# Save report to specific file
./run_validator.sh --output /path/to/report.txt

# Enable verbose output
./run_validator.sh --verbose
```

### Direct Python Usage

```bash
python3 validate_selectors.py --url http://localhost:5173 --output report.txt
```

## Report Format

The tool generates a detailed report with the following sections:

### Summary
```
============================================================
Selector Validation Report
============================================================
Generated: 2026-03-20 14:30:45
Application: http://localhost:5173

Summary
----------------------------------------
Total Selectors:  50
Valid:            45 (90.0%)
Invalid:          5 (10.0%)
```

### Invalid Selectors
```
Invalid Selectors
----------------------------------------

1. .parameters-table-container
   Reason: Element not found
   Used in: AN-005 (Parameter Table Test), AN-010 (Parameter Filter Test)
   💡 Suggestion: Check if class name has changed or is dynamically generated
```

### Recommendations
```
Recommendations
----------------------------------------
⚠️  MEDIUM: More than 10% of selectors are invalid.
   Action: Fix invalid selectors before running tests.
```

### Common Issues
```
Common Issues Detected
----------------------------------------
• Complex class selector: 3 occurrences
• Single element selector: 2 occurrences
```

## Output

Reports are automatically saved to:
```
.claude/skills/event2table-universal-test/output/selector_validation_YYYYMMDD_HHMMSS.txt
```

## Common Selector Issues

### 1. Pseudo-elements/classes
```css
/* ❌ May not work */
.element::before
.button:active

/* ✅ Better */
.element
.button.active
```

### 2. Complex Class Selectors
```css
/* ❌ Too specific */
.container.inner.wrapper.box

/* ✅ Use ID or simpler class */
#main-container
.main-wrapper
```

### 3. Attribute Selectors
```css
/* ❌ Fragile */
[data-testid="submit-button"][type="submit"]

/* ✅ Add test-specific classes */
.test-submit-button
```

### 4. Dynamically Generated Classes
```css
/* ❌ Changes on every build */
.css-123456789-button

/* ✅ Use stable classes */
.primary-button
.btn-submit
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Validate Selectors

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install agent-browser
        run: npm install -g @agent-browser/cli

      - name: Start application
        run: npm run dev &
        working-directory: ./frontend

      - name: Wait for app
        run: sleep 10

      - name: Run validator
        run: |
          cd .claude/skills/event2table-universal-test/scripts
          python3 validate_selectors.py --url http://localhost:5173

      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: selector-validation-report
          path: .claude/skills/event2table-universal-test/output/*.txt
```

## Troubleshooting

### agent-browser not found
```bash
npm install -g @agent-browser/cli
```

### Application not running
```bash
# Start the development server
cd frontend
npm run dev
```

### Timeout errors
- Check if the application is responsive
- Increase timeout in `validate_selectors.py` (line 155)
- Verify network connectivity

### Permission denied
```bash
chmod +x run_validator.sh
chmod +x validate_selectors.py
```

## Development

### Adding New Checks

Edit `validate_selectors.py` to add custom validation logic:

```python
def custom_check(self, selector: str) -> Tuple[bool, str]:
    """Add custom validation logic"""
    if selector.startswith('.test-'):
        return True, "Test selector verified"
    return False, "Not a test selector"
```

### Extending Reports

Modify the `generate_report()` method to add new sections:

```python
def generate_report(self) -> str:
    report = []
    # ... existing code ...

    # Add custom section
    report.append("Custom Metrics")
    report.append("-" * 40)
    report.append(f"Custom metric: {self.custom_metric}")

    return "\n".join(report)
```

## Configuration

### Environment Variables

- `BROWSER_URL`: Default application URL (default: `http://localhost:5173`)
- `VALIDATOR_TIMEOUT`: Selector check timeout in seconds (default: 10)
- `VALIDATOR_OUTPUT_DIR`: Output directory for reports (default: `./output`)

### Test Configuration Location

The tool looks for test configurations in:
```
.claude/skills/event2table-universal-test/config/test_configs/*.json
```

## Contributing

To contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Create an issue in the repository
- Check existing documentation
- Review test configuration examples

## Version History

- **1.0.0** (2026-03-20): Initial release
  - Automated selector validation
  - agent-browser integration
  - Detailed reporting
  - Fix suggestions
  - Multi-environment support

## Related Tools

- [Universal Test Executor](../README.md): Main test execution framework
- [Test Config Generator](./generate_test_configs.py): Generate test configurations
- [Coverage Analyzer](./analyze_coverage.py): Analyze test coverage

---

**Author**: Event2Table Test System
**Version**: 1.0.0
**Last Updated**: 2026-03-20
