---
name: event2table-e2e-test
description: Enterprise-grade intelligent E2E testing system for Event2Table project using Chrome DevTools MCP. Use when Claude needs to: (1) Run comprehensive E2E tests on Event2Table web application, (2) Generate test configurations automatically using AI, (3) Predict high-risk code areas and suggest tests, (4) Monitor performance and detect regressions, (5) Generate comprehensive quality reports with multi-dimensional scoring. The skill provides intelligent test data generation, adaptive retry mechanisms, and integration with existing test infrastructure.
---

# Event2Table E2E Testing Skill

## Quick Start

Execute full E2E test suite:
```
Invoke this skill when user asks to run tests, verify functionality, or check system health.
```

## Testing Modes

### Single Execution (Default)
Run complete test suite once and generate report.

**Use when**: CI/CD validation, pre-commit checks, manual verification

### Watch Mode
Monitor file changes and auto-run affected tests.

**Use when**: Development context detected in prompt ("working on X feature", "developing Y")

**Detection**: Prompt contains development keywords → Auto-switch to watch mode

## Module-Based Testing

Tests are organized by module:

- **Analytics** (`/games`, `/events`, `/parameters`, `/dashboard`) - 30+ tests
- **Event Builder** (`/event-node-builder`, `/field-builder`) - 20+ tests
- **Canvas** (`/canvas`, `/flow-builder`) - 15+ tests

Run specific module:
```
"Test the analytics module"
"Run event builder tests"
"Verify canvas functionality"
```

## Intelligent Features

### 🤖 AI Test Generator
Automatically generates test configurations by analyzing page structure.

**Trigger**: "Generate tests for [page/url]", "Create test config for [module]"

**Output**: JSON test configuration with steps, assertions, and expected results

### 🔮 Defect Prediction
Predicts high-risk code areas based on Git history, complexity, and bug density.

**Trigger**: "Analyze code risk", "Predict defects", "What needs testing?"

**Output**: Risk scores, recommendations, suggested test priority

### 📊 Performance Monitoring
Tracks Core Web Vitals (LCP, FID, CLS) and custom metrics with regression detection.

**Trigger**: "Check performance", "Run performance tests", "Any performance issues?"

**Output**: Performance report with regression alerts and blame analysis

### ⭐ Quality Scoring
Multi-dimensional scoring: test coverage (25%), pass rate (25%), performance (20%), code quality (15%), security (10%), accessibility (5%).

**Trigger**: "Quality report", "System health check", "How's the code quality?"

**Output**: Overall grade (A-F), dimension scores, trends, recommendations

### 🎲 Smart Test Data Generation
Generates boundary values, edge cases, production-like data, and fuzzing data.

**Trigger**: "Generate test data", "Create test fixtures", "Need test data for X"

**Output**: Comprehensive test data sets with coverage analysis

## Test Execution Workflow

1. **Pre-flight Checks**
   - Verify frontend server running (http://localhost:5173)
   - Verify backend server running (http://127.0.0.1:5001)
   - Check database connectivity
   - Validate test data integrity

2. **Test Execution**
   - Load test configuration
   - Execute tests by priority (critical → high → medium)
   - Adaptive retry on failures
   - Collect screenshots and metrics

3. **Validation**
   - React Query cache state
   - DOM element presence and visibility
   - Route state correctness
   - Console error detection
   - Network request validation

4. **Post-test**
   - Generate reports (Markdown + JSON)
   - Update performance baseline
   - Store screenshots
   - Calculate quality scores

## Error Handling

### Auto-fixable Issues
- Timeout → Increase wait time and retry
- Element not found → Refresh DOM and retry
- Network glitch → Wait and retry

### Requires Code Fix
- React Hooks errors → Report and suggest fix
- API contract mismatch → Document in report
- Component crash → Screenshot + error details

## Output

### Reports Location
- Markdown: `output/reports/markdown/`
- JSON: `output/reports/json/`
- Screenshots: `output/screenshots/`

### Report Contents
- Test summary (pass/fail/skip)
- Performance metrics
- Quality scores (A-F grade)
- Regression alerts
- Recommendations
- Blame analysis (who broke what)

## Configuration Files

- **Test configs**: `config/test-configs.json`
- **Module tests**: `config/*-tests.json`
- **Settings**: `config/skill-settings.json`
- **Error patterns**: `data/error-patterns.json`
- **Performance baseline**: `data/performance-baseline.json`

## Advanced Features

See detailed documentation:

- **AI Test Generator**: [references/AI_TEST_GENERATOR.md](references/AI_TEST_GENERATOR.md)
- **Defect Prediction**: [references/DEFECT_PREDICTION.md](references/DEFECT_PREDICTION.md)
- **Performance Monitoring**: [references/PERFORMANCE_MONITORING.md](references/PERFORMANCE_MONITORING.md)
- **Quality Scoring**: [references/QUALITY_SCORING.md](references/QUALITY_SCORING.md)
- **Test Data Generation**: [references/TEST_DATA_GENERATION.md](references/TEST_DATA_GENERATION.md)

## Scripts

Available helper scripts:

- `scripts/generate_tests.js` - AI test generation
- `scripts/predict_risks.py` - Defect prediction
- `scripts/monitor_performance.js` - Performance tracking
- `scripts/calculate_quality.js` - Quality scoring
- `scripts/generate_test_data.js` - Test data generation

## Important Notes

- **STAR001 Protection**: Never use GID 10000147 for write operations
- **Test GID Range**: Use 90000000+ for safe testing
- **Database Isolation**: Tests use `data/test_database.db`
- **Game Context**: Always pass `game_gid` parameter in API calls
