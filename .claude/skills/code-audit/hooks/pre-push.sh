#!/bin/bash
# Pre-push hook for code audit

# Run full code audit before push
echo "Running full code audit..."

python3 .claude/skills/code-audit/hooks/run_audit.py

# Check exit code
if [ $? -ne 0 ]; then
    echo "❌ Code audit failed. Push aborted."
    echo "Run '/code-audit' to see issues and fix them before pushing."
    exit 1
fi

echo "✅ Code audit passed"
exit 0
