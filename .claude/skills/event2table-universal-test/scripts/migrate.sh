#!/bin/bash

# Migration script: Convert MCP tests to agent-browser format
# Source: /Users/mckenzie/Documents/event2table/.claude/skills/event2table-e2e-test
# Target: /Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILL="/Users/mckenzie/Documents/event2table/.claude/skills/event2table-e2e-test"
TARGET_SKILL="/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test"

echo "🚀 Starting test migration..."
echo "Source: $SOURCE_SKILL"
echo "Target: $TARGET_SKILL"
echo ""

# Create output directories
mkdir -p "$TARGET_SKILL/tests/regression"
mkdir -p "$TARGET_SKILL/tests/e2e"
mkdir -p "$TARGET_SKILL/output/screenshots"

echo "📁 Directory structure created"
echo ""

# Function to convert MCP action to agent-browser command
convert_action() {
    local action=$1
    case $action in
        "navigate")
            echo "open"
            ;;
        "wait_for")
            echo "wait"
            ;;
        "take_screenshot")
            echo "screenshot"
            ;;
        "validate_state")
            echo "validate"
            ;;
        "fill")
            echo "fill"
            ;;
        "click")
            echo "click"
            ;;
        *)
            echo "$action"
            ;;
    esac
}

# Extract tests from source config
echo "📋 Extracting tests from analytics-tests.json..."

if [ -f "$SOURCE_SKILL/config/analytics-tests.json" ]; then
    # Use Python to parse and convert JSON
    python3 - <<EOF
import json
import os

source_file = "$SOURCE_SKILL/config/analytics-tests.json"
target_dir = "$TARGET_SKILL/tests/regression"

with open(source_file, 'r') as f:
    data = json.load(f)

test_count = 0
for test in data.get('tests', []):
    test_id = test.get('id', 'UNKNOWN')
    test_name = test.get('name', 'Unnamed Test')
    test_url = test.get('url', '')
    test_priority = test.get('priority', 'medium')

    # Convert steps
    steps = []
    for step in test.get('steps', []):
        action = step.get('action', '')
        new_action = action

        # Convert actions
        if action == 'navigate':
            steps.append({
                "action": "open",
                "url": step.get('url', test_url)
            })
        elif action == 'wait_for':
            condition = step.get('selector', '')
            if 'selector' in step:
                steps.append({
                    "action": "wait",
                    "condition": {"selector": step.get('selector')},
                    "timeout": step.get('timeout', 5000)
                })
            else:
                steps.append({
                    "action": "wait",
                    "condition": {"load": "networkidle"},
                    "timeout": step.get('timeout', 5000)
                })
        elif action == 'validate_state':
            checks = step.get('checks', [])
            converted_checks = []
            for check in checks:
                check_type = check.get('type', '')
                if check_type == 'console_errors':
                    converted_checks.append({
                        "type": "console_clean",
                        "level": "error"
                    })
                elif check_type == 'element_exists':
                    converted_checks.append({
                        "type": "element_exists",
                        "selector": check.get('selector', '')
                    })
                elif check_type == 'text_contains':
                    converted_checks.append({
                        "type": "text_contains",
                        "selector": check.get('selector', ''),
                        "text": check.get('text', '')
                    })

            if converted_checks:
                steps.append({
                    "action": "validate",
                    "checks": converted_checks
                })
        elif action == 'take_screenshot':
            screenshot_name = step.get('name', 'screenshot')
            steps.append({
                "action": "screenshot",
                "path": f"output/screenshots/regression/{screenshot_name}.png"
            })

    # Create new test config
    new_test = {
        "id": test_id,
        "name": test_name,
        "type": "regression",
        "priority": test_priority,
        "engine": "agent-browser",
        "url": test_url,
        "timeout": 10000,
        "steps": steps
    }

    # Write to file
    filename = f"{test_id.lower().replace('-', '_')}.json"
    output_path = os.path.join(target_dir, filename)

    with open(output_path, 'w') as f:
        json.dump(new_test, f, indent=2)

    test_count += 1
    print(f"  ✓ Migrated: {test_id} - {test_name}")

print(f"\n✅ Total tests migrated: {test_count}")
EOF
else
    echo "⚠️  Warning: Source file not found at $SOURCE_SKILL/config/analytics-tests.json"
    echo "Creating sample tests instead..."

    # Create sample tests
    cat > "$TARGET_SKILL/tests/regression/reg_001_dashboard_load.json" <<'EOF'
{
  "id": "REG-001",
  "name": "Dashboard Load Test",
  "type": "regression",
  "priority": "critical",
  "engine": "agent-browser",
  "url": "http://localhost:5173/",
  "timeout": 10000,
  "steps": [
    {
      "action": "open",
      "url": "http://localhost:5173/"
    },
    {
      "action": "wait",
      "condition": { "load": "networkidle" }
    },
    {
      "action": "validate",
      "checks": [
        { "type": "element_exists", "selector": ".dashboard-container" },
        { "type": "console_clean", "level": "error" }
      ]
    },
    {
      "action": "screenshot",
      "path": "output/screenshots/regression/dashboard.png"
    }
  ]
}
EOF

    cat > "$TARGET_SKILL/tests/regression/reg_002_games_list.json" <<'EOF'
{
  "id": "REG-002",
  "name": "Games List Display",
  "type": "regression",
  "priority": "critical",
  "engine": "agent-browser",
  "url": "http://localhost:5173/games",
  "timeout": 10000,
  "steps": [
    {
      "action": "open",
      "url": "http://localhost:5173/games"
    },
    {
      "action": "wait",
      "condition": { "selector": ".games-grid" }
    },
    {
      "action": "validate",
      "checks": [
        { "type": "element_exists", "selector": ".games-grid" },
        { "type": "element_exists", "selector": "input[placeholder*='搜索']" },
        { "type": "console_clean", "level": "error" }
      ]
    },
    {
      "action": "screenshot",
      "path": "output/screenshots/regression/games-list.png"
    }
  ]
}
EOF

    echo "  ✓ Created sample tests: REG-001, REG-002"
fi

echo ""
echo "✅ Migration complete!"
echo ""
echo "📁 Migrated tests location: $TARGET_SKILL/tests/regression/"
echo "📊 Next steps:"
echo "  1. Review migrated tests"
echo "  2. Run tests using the skill"
echo "  3. Verify results"
echo ""
