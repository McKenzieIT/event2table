# Event2Table E2E Testing Skill

Enterprise-grade intelligent E2E testing system for Event2Table project using Chrome DevTools MCP.

## Features

- 🤖 **AI Test Generator** - Automatically generates test configurations
- 🔮 **Defect Prediction** - Predicts high-risk code areas
- 📊 **Performance Monitoring** - Tracks Core Web Vitals with regression detection
- ⭐ **Quality Scoring** - Multi-dimensional scoring (6 dimensions)
- 🎲 **Smart Test Data** - Generates boundary values, edge cases, production-like data

## Quick Start

```bash
# Invoke the skill when user asks to run tests
"Run E2E tests for Event2Table"
"Test the analytics module"
"Check performance and generate report"
```

## Module Testing

- **Analytics** - 30+ tests (`/games`, `/events`, `/parameters`, `/dashboard`)
- **Event Builder** - 20+ tests (`/event-node-builder`, `/field-builder`)
- **Canvas** - 15+ tests (`/canvas`, `/flow-builder`)

## Output

- Reports: `output/reports/` (Markdown + JSON)
- Screenshots: `output/screenshots/`
- Traces: `output/traces/`

## Configuration

Edit `config/skill-settings.json` to customize:
- Server URLs
- Test timeouts
- Performance thresholds
- Quality targets

## Version

2.0.0 - Enterprise Edition with AI-powered testing
