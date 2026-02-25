#!/bin/bash
# Run integration tests with database

echo "==================================="
echo "Parameter Management Integration Tests"
echo "==================================="
echo ""

# Set test environment
export FLASK_ENV=testing
export ENVIRONMENT=testing

# Run integration tests
pytest backend/tests/integration/ \
    --tb=short \
    -v \
    --strict-markers \
    -m "integration" \
    "$@"

# Exit with pytest's exit code
exit $?
