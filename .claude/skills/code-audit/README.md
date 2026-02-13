# Code Audit Skill

Comprehensive code quality audit tool for Event2Table project.

## Features

### Compliance Detectors
- **Game GID Check**: Enforces game_gid vs game_id usage rules
- **API Contract Check**: Validates frontend-backend API consistency
- **TDD Check**: Ensures test files exist for all source files

### Security Detectors
- **SQL Injection**: Detects SQL injection vulnerabilities
- **XSS Protection**: Detects missing XSS protection

### Quality Detectors
- **Complexity Analysis**: Measures cyclomatic complexity
- **Code Duplication**: Detects duplicate code blocks

## Usage

### Run Full Audit
```
/code-audit
```

### Run Quick Audit
```
/code-audit --quick
```

### Run Specific Detectors
```
/code-audit --detectors game_gid,sql_injection
```

## Output

Reports are generated in `.claude/skills/code-audit/output/reports/`:
- `audit_report.md` - Markdown report
- `audit_report.json` - JSON report

## Git Hooks

Pre-commit and pre-push hooks are available:
```bash
python3 scripts/setup/setup_code_audit_hooks.py
```
