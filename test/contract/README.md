# API Contract Testing Framework

Automated scanning framework to detect inconsistencies between frontend API calls and backend routes.

## Overview

This framework provides two scanners:

1. **Backend Route Scanner** (`contract_scanner.py`) - Extracts all Flask routes
2. **Frontend API Call Scanner** (`frontend_scanner.py`) - Extracts all frontend API calls

## Usage

### Backend Scanning

```bash
# Basic scan (uses web_app.py)
python test/contract/contract_scanner.py

# Verbose output with route summary
python test/contract/contract_scanner.py --verbose

# Custom output path
python test/contract/contract_scanner.py --output custom_routes.json

# Custom app path
python test/contract/contract_scanner.py --app path/to/app.py
```

### Frontend Scanning

```bash
# Basic scan (uses frontend/src)
python test/contract/frontend_scanner.py

# Verbose output with call summary
python test/contract/frontend_scanner.py --verbose

# Custom output path
python test/contract/frontend_scanner.py --output custom_calls.json

# Custom frontend path
python test/contract/frontend_scanner.py --frontend-path path/to/src
```

## Output Format

### Backend Routes (`backend_routes.json`)

```json
{
  "/api/games": {
    "endpoint": "games.games_bp",
    "methods": ["GET", "POST"],
    "parameters": []
  },
  "/api/games/<int:game_gid>": {
    "endpoint": "games.games_bp",
    "methods": ["GET", "PUT", "DELETE"],
    "parameters": ["game_gid"]
  }
}
```

### Frontend Calls (`frontend_calls.json`)

```json
{
  "features/games/api.ts": [
    {
      "line": 42,
      "method": "GET",
      "path": "/api/games",
      "type": "fetch"
    }
  ],
  "features/events/EventsList.tsx": [
    {
      "line": 15,
      "method": "DELETE",
      "path": "/api/games/<int:game_gid>",
      "type": "fetch"
    }
  ]
}
```

## Contract Validation

After scanning both backend and frontend, use the contract validation script:

```bash
# Run validation (checks for mismatches)
python test/contract/validate_contracts.py

# Auto-fix simple issues
python test/contract/validate_contracts.py --fix

# Verbose output
python test/contract/validate_contracts.py --verbose
```

## Common Issues Detected

1. **Missing Backend Routes** - Frontend calls API that doesn't exist
2. **Method Mismatch** - Frontend uses POST but backend only has GET
3. **Parameter Mismatch** - Frontend uses `game_id` but backend expects `game_gid`

## Examples

### Finding Orphaned Frontend Calls

```python
# Load fixtures
with open('test/contract/fixtures/backend_routes.json') as f:
    backend_routes = json.load(f)

with open('test/contract/fixtures/frontend_calls.json') as f:
    frontend_calls = json.load(f)

# Find calls without matching backend route
for file_path, calls in frontend_calls.items():
    for call in calls:
        if call['path'] not in backend_routes:
            print(f"⚠️  No backend route for: {call['method']} {call['path']}")
            print(f"   Found in: {file_path}:{call['line']}")
```

## Troubleshooting

### Backend Scanner Issues

**Error**: `Flask app not found in module`
- **Solution**: Ensure the app file exports a Flask app named `app`
- **Check**: `app = Flask(__name__)` in your app file

### Frontend Scanner Issues

**Error**: `Frontend path not found`
- **Solution**: Ensure frontend/src directory exists
- **Check**: `ls frontend/src`

**Warning**: `API client calls (need manual review)`
- **Solution**: Some API patterns are complex and need manual inspection
- **Review**: Check the raw line output for unknown calls

## Maintenance

### Adding New API Patterns

To support new API call patterns, update `frontend_scanner.py`:

```python
def _find_custom_api_calls(self, lines: List[str]) -> List[Dict[str, Any]]:
    """Add custom API call patterns"""
    calls = []
    pattern = r'your_pattern_here'

    for line_num, line in enumerate(lines, 1):
        matches = re.finditer(pattern, line)
        for match in matches:
            calls.append({
                "path": match.group(1),
                "method": "GET",  # Extract from match
                "line": line_num,
                "type": "custom"
            })

    return calls
```

## Integration with CI/CD

Add to pre-commit hook:

```bash
# .git/hooks/pre-commit
python test/contract/contract_scanner.py
python test/contract/frontend_scanner.py
python test/contract/validate_contracts.py

if [ $? -ne 0 ]; then
    echo "❌ API contract validation failed"
    exit 1
fi
```
