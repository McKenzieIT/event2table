#!/bin/bash
# Run unit tests with coverage

echo "==================================="
echo "Parameter Management Unit Tests"
echo "==================================="
echo ""

# Set test environment
export FLASK_ENV=testing
export ENVIRONMENT=testing

# Run tests with coverage
pytest backend/tests/unit/ \
    --cov=backend/domain/models \
    --cov=backend/domain/services \
    --cov=backend/application/dtos \
    --cov=backend/application/services \
    --cov-report=html:backend/tests/output/coverage/html \
    --cov-report=term-missing \
    --cov-report=json:backend/tests/output/coverage/coverage.json \
    --tb=short \
    -v \
    --strict-markers \
    "$@"

# Exit with pytest's exit code
exit $?
