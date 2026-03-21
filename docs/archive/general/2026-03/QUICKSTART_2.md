# CI/CD Quick Start Guide

**For**: Event2Table Developers
**Last Updated**: 2026-03-18

---

## Quick Reference

### Run Tests Locally

```bash
# Backend tests
source backend/venv/bin/activate
pytest backend/tests/unit/ -v

# Frontend tests
cd frontend
npm run test:unit

# E2E tests
cd frontend
npm run test:e2e:smoke

# All CI/CD tests
pytest test/ci_cd/ -v
```

### Deployment Commands

```bash
# Deploy to production
./scripts/deploy.sh deploy

# Create backup only
./scripts/deploy.sh backup

# Health check
./scripts/deploy.sh health-check

# Rollback
./scripts/deploy.sh rollback
```

### Monitoring Commands

```bash
# Run all checks
./scripts/monitoring/performance_monitor.sh

# Cache monitoring
./scripts/monitoring/performance_monitor.sh --cache

# API monitoring
./scripts/monitoring/performance_monitor.sh --api

# Database monitoring
./scripts/monitoring/performance_monitor.sh --database

# Resource monitoring
./scripts/monitoring/performance_monitor.sh --resources

# Generate report
./scripts/monitoring/performance_monitor.sh --report
```

---

## CI/CD Pipeline Stages

```
1. Push/PR → GitHub Actions
   ├─ Backend Unit Tests (10 min)
   ├─ Frontend Unit Tests (10 min)
   ├─ E2E Tests (20 min)
   ├─ Lighthouse CI (15 min)
   ├─ Code Quality (10 min)
   └─ API Contract Tests (10 min)

2. All Tests Pass → Deploy (main only)
   ├─ Create Backup
   ├─ Deploy Application
   ├─ Health Check (5 min)
   ├─ Smoke Tests
   └─ Rollback on Failure

3. Deploy Success → Monitor
   ├─ Cache Performance
   ├─ API Response Times
   ├─ Database Queries
   └─ System Resources
```

---

## Common Workflows

### Feature Development

```bash
# 1. Start feature branch
git checkout -b feature/new-feature

# 2. Develop
# ... write code ...

# 3. Test locally
pytest test/ci_cd/ -v
npm run test:all

# 4. Commit
git add .
git commit -m "feat: add new feature"

# 5. Push and create PR
git push origin feature/new-feature
# CI/CD runs automatically

# 6. Merge after approval
# Deploy runs automatically on main
```

### Hotfix Deployment

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug

# 2. Quick fix and test
pytest test/ci_cd/ -v --fast

# 3. Deploy to production
git push origin hotfix/critical-bug
# Create PR, merge, auto-deploy

# 4. Monitor
./scripts/monitoring/performance_monitor.sh --report
```

### Rollback

```bash
# Automatic rollback on failure
# Manual rollback if needed:
./scripts/deploy.sh rollback

# Verify
./scripts/deploy.sh health-check
```

---

## Performance Thresholds

| Metric                | Target   | Alert   |
|-----------------------|----------|---------|
| Cache Hit Rate        | ≥80%     | <70%    |
| API Response Time     | ≤1000ms  | >1500ms |
| Database Query Time   | ≤500ms   | >750ms  |
| CPU Usage             | ≤80%     | >90%    |
| Memory Usage          | ≤80%     | >90%    |
| Disk Usage            | ≤80%     | >90%    |

---

## File Locations

| Component            | Path                                     |
|----------------------|------------------------------------------|
| CI/CD Workflow       | `.github/workflows/ci-cd.yml`            |
| Deployment Script    | `scripts/deploy.sh`                      |
| Monitoring Script    | `scripts/monitoring/performance_monitor.sh` |
| Test Suites          | `test/ci_cd/`                            |
| Deployment Logs      | `logs/deployments/`                      |
| Monitoring Reports   | `reports/monitoring/`                    |
| Backups              | `backups/`                               |

---

## Environment Variables

```bash
# Required for deployment
export DEPLOY_KEY="your-deploy-key"
export DATABASE_URL="sqlite:///data/dwd_generator.db"
export API_TOKEN="your-api-token"

# Optional
export SLACK_WEBHOOK="https://hooks.slack.com/..."
```

---

## Troubleshooting

### Tests Fail

```bash
# Check what failed
pytest test/ci_cd/ -v --tb=short

# Run specific test
pytest test/ci_cd/test_ci_cd_workflow.py::TestGitHubActionsWorkflow::test_workflow_file_exists -v
```

### Deployment Fails

```bash
# Check logs
cat logs/deployments/deploy_*.log | tail -100

# Manual rollback
./scripts/deploy.sh rollback

# Verify health
./scripts/deploy.sh health-check
```

### Performance Issues

```bash
# Generate report
./scripts/monitoring/performance_monitor.sh --report

# Check specific metric
./scripts/monitoring/performance_monitor.sh --cache
./scripts/monitoring/performance_monitor.sh --api
```

---

## GitHub Actions Status

Check workflow status:
```
https://github.com/YOUR_ORG/event2table/actions
```

View workflow runs:
```
https://github.com/YOUR_ORG/event2table/actions/workflows/ci-cd.yml
```

---

## Useful Commands

```bash
# Check last deployment
cat logs/deployments/last_deployment.txt

# Check current version
cat logs/deployments/current_version.txt

# List backups
ls -lh backups/

# Find recent deployment logs
ls -lt logs/deployments/ | head -5

# Monitor in real-time
tail -f logs/backend.log
tail -f logs/deployments/deploy_*.log

# Check test coverage
pytest test/ci_cd/ --cov=test/ci_cd --cov-report=html
open htmlcov/index.html
```

---

## Getting Help

1. **Documentation**: `docs/ci-cd/README.md`
2. **Tests**: `test/ci_cd/`
3. **Logs**: `logs/deployments/`
4. **GitHub Issues**: Create issue for bugs

---

## Checklist

Before deploying to production:

- [ ] All tests pass locally
- [ ] Test coverage ≥80%
- [ ] E2E tests pass
- [ ] Lighthouse scores ≥90
- [ ] Code quality checks pass
- [ ] Performance metrics OK
- [ ] Backup created
- [ ] Rollback plan ready

---

**Remember**:
- ✅ Tests must pass before merge
- ✅ Auto-deploy only on main branch
- ✅ Auto-rollback on failure
- ✅ Monitor after deployment

**Need help?** Check `docs/ci-cd/README.md` for detailed documentation.
