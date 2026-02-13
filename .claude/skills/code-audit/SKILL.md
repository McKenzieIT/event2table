---
name: code-audit
description: Comprehensive code quality audit tool for Event2Table project. Enforces game_gid compliance, checks API contracts, validates TDD compliance, detects security vulnerabilities (SQL injection, XSS), and analyzes code quality (complexity, duplication).
---

# Code Audit Skill

## When to Use

Use this skill when:
- Reviewing code before committing
- Checking for compliance with Event2Table standards
- Performing security audits
- Analyzing code quality
- Validating API contracts between frontend and backend

## Quick Start

Simply invoke:
```
/code-audit
```

## What It Does

The code-audit skill runs a comprehensive analysis of your codebase:

1. **Compliance Checks**
   - Enforces game_gid usage (critical for Event2Table)
   - Validates frontend-backend API contracts
   - Checks TDD compliance

2. **Security Scanning**
   - Detects SQL injection vulnerabilities
   - Identifies XSS protection gaps

3. **Quality Analysis**
   - Measures cyclomatic complexity
   - Detects code duplication

## Modes

- **Quick Mode** (`--quick`): Only critical compliance checks (~1 minute)
- **Standard Mode** (`--standard`): Compliance + security (~3 minutes)
- **Deep Mode** (`--deep` or default): All checks + trend analysis (~10 minutes)

## Output

Reports are generated in:
- `.claude/skills/code-audit/output/reports/audit_report.md`
- `.claude/skills/code-audit/output/reports/audit_report.json`

## Project Root

The skill operates from: /Users/mckenzie/Documents/event2table
