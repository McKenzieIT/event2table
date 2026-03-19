---
name: code-audit
description: Code quality, security, and compliance auditing. ALWAYS use this skill when users mention: code review, audit, check, validate, verify, security, vulnerability, SQL injection, XSS, compliance, standards, TDD, code quality, complexity, duplication, or API contracts. Trigger for queries about: checking code before committing, security scanning, vulnerability detection, enforcing coding standards, validating against project rules, or analyzing code quality. Use even when code review/audit is mentioned incidentally or as a secondary concern. If the query contains words like "review", "check", "audit", "validate", "secure", "safe", "compliant", or "quality", consult this skill.
---

# Code Audit Skill

## When to Use

Use this skill when:
- Reviewing code before committing
- Checking for compliance with Event2Table standards
- Performing security audits
- Analyzing code quality
- Validating API contracts between frontend and backend
- **Detecting performance issues** (N+1 queries, missing cache decorators, React optimization)
- **Enforcing React Hooks rules**
- **Validating GraphQL type synchronization**

## Quick Start

Simply invoke:
```
/code-audit
```

## What It Does

The code-audit skill runs a comprehensive analysis of your codebase:

### Phase 1 Detectors (Original - 3 categories)
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

### Phase 2 Detectors (NEW - 4 categories) ⭐
4. **Performance Optimization Checks** 🆕
   - **Cache Decorator Check** (85 known issues)
     - Detects missing `@cached` decorators on Service query methods
     - Detects missing `@cache_invalidate` decorators on write operations
     - Validates cache TTL ranges (300-1800 seconds recommended)

   - **N+1 Query Check** (530 known issues)
     - Detects database queries inside for/while loops
     - Identifies missing JOIN operations for related data
     - Flags batch operations that should use IN (...)

5. **React Best Practices Checks** 🆕
   - **React Hooks Check** (213 known issues)
     - Ensures all Hooks are called before conditional returns
     - Prevents Hooks inside if/for/nested functions
     - Validates Hook call order consistency

   - **React Performance Check** (213 known issues)
     - Detects large components (>500 chars) missing React.memo
     - Identifies expensive operations missing useMemo
     - Flags useEffect dependencies missing useCallback

### Planned Phase 3 Detectors (Future)
6. **GraphQL Ecosystem Checks**
   - GraphQL type synchronization (frontend enums vs backend schema)
   - Pydantic model completeness (Service layer field access)

7. **Architecture Compliance Checks**
   - Entity architecture patterns (Repository returns Entity, not Dict)
   - Completeness principle (no pass/TODO/placeholder implementations)

## Modes

- **Quick Mode** (`--quick`): Only critical compliance checks (~1 minute)
- **Standard Mode** (`--standard`): Compliance + security (~3 minutes)
- **Deep Mode** (`--deep` or default): All checks including performance optimization (~10 minutes)

## Output

Reports are generated in:
- `.claude/skills/code-audit/output/reports/audit_report.md`
- `.claude/skills/code-audit/output/reports/audit_report.json`

## Coverage Statistics

| Category | Detectors | Known Issues | Coverage |
|----------|-----------|--------------|----------|
| Compliance | 3 | Unknown | 100% |
| Security | 2 | Unknown | 100% |
| Quality | 2 | Unknown | 100% |
| **Performance** | **2** | **615** (85+530) | **67%** |
| **React** | **2** | **213** | **67%** |
| **Total** | **11** | **828+** | **67%** |

**Target**: 100% coverage after Phase 3 implementation

## Project Root

The skill operates from: /Users/mckenzie/Documents/event2table

## Version History

- **v2.0** (2026-02-24): Initial release with 7 detectors
- **v3.0** (2026-03-13): Phase 2 upgrade - Added 4 performance/React detectors, 67% coverage
- **v4.0** (Future): Phase 3 - GraphQL and Architecture detectors, 100% coverage
