# GitHub Actions Workflows

This directory contains GitHub Actions workflow configurations for continuous integration and continuous deployment (CI/CD).

## Workflows

### Frontend CI (`frontend-ci.yml`)

**Purpose**: Automated type checking, linting, and testing for frontend code

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`
- Changes to `frontend/**` or `.github/workflows/frontend-ci.yml`

**Jobs**:

1. **TypeScript Type Check**
   - Runs `npm run type-check`
   - Ensures type safety with strict TypeScript configuration
   - Catches type errors before they reach production

2. **ESLint**
   - Runs `npm run lint`
   - Enforces code style and best practices
   - Reports unused variables, potential bugs, and code smells

3. **Unit Tests**
   - Runs `npm run test:unit`
   - Executes Vitest unit tests
   - Uploads coverage reports as artifacts

## Local Development

### Before Committing

Always run these commands to ensure your code passes CI:

```bash
cd frontend

# Type check
npm run type-check

# Lint
npm run lint

# Unit tests
npm run test:unit

# All at once
npm run type-check && npm run lint && npm run test:unit
```

### CI fails locally?

1. Fix the errors reported
2. Re-run the failing command to verify
3. Commit and push your changes
4. GitHub Actions will re-run automatically

## Workflow Status

Check workflow status at:
```
https://github.com/YOUR_ORG/event2table/actions
```

## Adding New Workflows

When adding new workflows:

1. Create a new `.yml` file in this directory
2. Follow GitHub Actions syntax: https://docs.github.com/en/actions
3. Test locally before pushing
4. Document triggers and jobs in this README

## Troubleshooting

### Workflow not running?

- Check if the file path matches the trigger paths
- Verify the workflow YAML syntax is correct
- Check GitHub Actions logs for errors

### Type check passes locally but fails on CI?

- Ensure Node.js version matches (v18)
- Clear npm cache: `npm ci`
- Check for environment-specific differences

## Related Documentation

- [TypeScript CI Guide](../../docs/development/TYPESCRIPT-CI-GUIDE.md)
- [TypeScript Quick Reference](../../docs/development/TYPESCRIPT-QUICK-REF.md)
- [Project Development Guide](../../CLAUDE.md)
