---
name: performance-audit
description: Performance optimization and bottleneck detection for applications. ALWAYS use this skill when users mention: slow/sluggish/laggy UI, loading delays, page speed issues, bundle size concerns, React performance, N+1 queries, database optimization, caching, API latency, or any performance-related terms. Trigger for: performance audits, profiling, bottleneck analysis, regression checks, pre-release validation, or optimization tasks. Use even when performance is mentioned incidentally or as a secondary concern. If the query contains words like "optimize", "slow", "fast", "performance", "lag", "delay", "loading time", or "response time", consult this skill.
---

# Performance Audit Skill

## Overview

Comprehensive performance analysis tool that combines **static code analysis** (preventive) and **runtime profiling** (diagnostic) to identify and fix performance bottlenecks across the entire Event2Table stack.

## Core Capabilities

### 1. Static Performance Analysis (Preventive)

Detects performance anti-patterns in code before they reach production:

**Frontend Detectors (Enhanced with Vercel Best Practices):**

**CRITICAL Priority (2-10× improvement):**
- **Async parallelization**: Sequential `await` → `Promise.all()` for independent operations
- **Bundle optimization**: Barrel imports, missing lazy loading for large components (>10KB)
- **Re-render optimization**: Derived state from continuous values, missing `startTransition`

**Existing Detection:**
- React optimization: Missing `React.memo`, `useMemo`, `useCallback`
- Bundle analysis: Large files, missing lazy-loading, code splitting
- Image optimization: Missing `loading="lazy"`, unoptimized images
- State management: Props drilling, unnecessary re-renders
- API usage: Non-parallelized requests, missing request caching

**Backend Detectors:**
- N+1 queries: Database queries inside loops
- Cache strategy: Missing `@cached` decorators on query functions
- Serialization: Large object transfers, missing field filtering
- Algorithm efficiency: O(n²) complexity, nested loops
- Async operations: Sequential operations that could be parallel

**Database Detectors:**
- Index usage: Missing indexes on JOIN/WHERE columns
- Query efficiency: `SELECT *`, unoptimized subqueries
- Transaction scope: Overly long transactions

**Configuration Detectors:**
- Build optimization: Missing code splitting, compression in Vite/Webpack
- Network: Missing gzip/brotli, improper cache headers
- CDN: Static assets not served via CDN
- Resource management: Memory leaks, connection pool limits

### 2. Runtime Performance Analysis (Diagnostic)

Measures actual performance to identify existing bottlenecks:

**Frontend Runtime:**
- Lighthouse metrics: FCP, LCP, TTI, FID, CLS
- Network waterfall: API call timing and parallelization
- Bundle analysis: Webpack bundle size and composition
- Render performance: FPS, interaction latency

**Backend Runtime:**
- API response times: P50, P95, P99 latencies
- Cache hit rates: Redis cache effectiveness
- Query performance: Slow query logs, execution plans
- CPU profiling: cProfile hotspot analysis

### 3. Automated Fix Application

Automatically applies safe performance optimizations:

**Auto-Fixed (Safe):**
- ✅ **NEW**: Parallelize sequential async operations with `Promise.all()`
- ✅ **NEW**: Replace barrel imports with direct imports
- ✅ **NEW**: Add lazy loading to large components (>10KB)
- ✅ Add `React.memo`, `useMemo`, `useCallback` to components
- ✅ Enable Vite code splitting and compression
- ✅ Add `@cached` decorators to query functions
- ✅ Add `loading="lazy"` to images
- ✅ Parallelize independent API calls

**Review-Required (Needs Validation):**
- ⚠️ Database index additions (need production data validation)
- ⚠️ Architectural changes (e.g., introducing virtual scrolling)
- ⚠️ CDN configuration (requires operations decision)

### 4. Performance Baselines & Regression Detection

- Establish performance baselines for key metrics
- Compare against baselines to detect regressions
- CI/CD integration for automated regression testing
- Trend analysis over time

### 5. Preventive Documentation

Automatically updates project documentation:
- Add performance rules to `CLAUDE.md`
- Create detailed optimization guides in `docs/performance/`
- Generate performance anti-patterns library
- Update code review checklists

## Modes

**Quick Mode** (`--quick`): Static analysis only (~5 minutes)
- Frontend React optimization check
- Backend N+1 query detection
- Basic configuration validation

**Standard Mode** (`--standard`): Static + CRITICAL detectors (~15 minutes)
- All quick mode checks
- **NEW**: Async parallelization detection (CRITICAL)
- **NEW**: Bundle optimization detection (CRITICAL)
- **NEW**: Re-render optimization detection (MEDIUM)
- Lighthouse audit on critical pages (planned)
- API response time sampling (planned)

**Deep Mode** (`--deep` or default): Complete analysis (~30-60 minutes)
- All standard mode checks
- Full Lighthouse audit on all pages
- Comprehensive API profiling
- Database query performance analysis
- Bundle analysis with visualization
- Performance regression detection
- Automated fix application

## Usage

```bash
# Run quick performance check
/performance-audit --quick

# Run standard analysis
/performance-audit --standard

# Run complete deep analysis with auto-fixes
/performance-audit --deep --apply-fixes

# Check for performance regression
/performance-audit --regression-check

# Generate performance baselines
/performance-audit --generate-baselines
```

## Output

Reports are generated in:
- `.claude/skills/performance-audit/output/reports/performance_report.md` (Markdown)
- `.claude/skills/performance-audit/output/reports/performance_report.html` (Interactive HTML)
- `.claude/skills/performance-audit/output/charts/` (Performance charts)

## Resources

### scripts/

**Main Entry Point:**
- `run_audit.py` - Orchestrates all detectors and analyzers

**Static Detectors:**
- `detectors/static/frontend_react.py` - React optimization detection (existing)
- `detectors/static/backend_queries.py` - N+1 query detection (existing)
- `detectors/static/config_optimization.py` - Build configuration detection (existing)
- `detectors/static/detector_async.py` - **NEW**: Async parallelization detection (Promise.all)
- `detectors/static/detector_bundle.py` - **NEW**: Bundle optimization detection
- `detectors/static/detector_rerender.py` - **NEW**: Re-render optimization detection
- `scripts/utils/ast_helpers.py` - **NEW**: AST analysis utilities

**Runtime Analyzers:**
- `detectors/runtime/lighthouse_runner.py` - Lighthouse integration
- `detectors/runtime/api_profiler.py` - API response time profiling
- `detectors/runtime/db_profiler.py` - Database query profiling

**Baseline Management:**
- `baselines/generate_baselines.py` - Create performance baselines
- `baselines/compare_baselines.py` - Regression detection

**Fix Application:**
- `fixers/apply_auto_fixes.py` - Apply automated fixes
- `fixers/generate_fix_suggestions.py` - Generate fix recommendations

**Reporters:**
- `reporters/markdown_reporter.py` - Generate Markdown reports
- `reporters/html_reporter.py` - Generate HTML visualization

### references/

- `frontend-patterns.md` - React performance optimization patterns
- `backend-patterns.md` - Backend performance optimization patterns
- `database-tuning.md` - Database tuning guide
- `anti-patterns.md` - Performance anti-patterns case library
- `claude-md-rules.md` - Performance rules for CLAUDE.md

### assets/

- `templates/performance_report.html` - HTML report template
- `templates/claude_md_section.md` - CLAUDE.md section template
- `config/baselines.json` - Default performance thresholds
- `config/thresholds.json` - Performance scoring thresholds

## Project Root

The skill operates from: `/Users/mckenzie/Documents/event2table`

## Integration with Code-Audit

**code-audit** focuses on:
- Security (SQL injection, XSS)
- Compliance (game_gid, TDD, API contracts)
- Code quality (complexity, duplication)

**performance-audit** focuses on:
- Runtime performance (response times, rendering speed)
- Resource efficiency (bundle size, query optimization)
- User experience (loading time, interaction lag)

Both skills can be run together for comprehensive code quality and performance validation.
