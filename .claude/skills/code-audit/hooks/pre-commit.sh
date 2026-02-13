#!/bin/bash
# Pre-commit hook for code audit

# Run quick code audit before commit
echo "Running code audit..."

python3 .claude/skills/code-audit/hooks/run_audit.py --quick

# Check exit code
if [ $? -ne 0 ]; then
    echo "❌ Code audit failed. Commit aborted."
    echo "Run '/code-audit' to see issues and fix them before committing."
    exit 1
fi

echo "✅ Code audit passed"
exit 0
