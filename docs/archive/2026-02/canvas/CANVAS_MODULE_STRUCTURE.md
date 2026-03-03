# Canvas Module Structure

## Overview

The Canvas system provides a visual node-based query building interface for the DWD Generator. It is located in `backend/services/canvas/` and provides both web pages and API endpoints for Canvas flow management.

## Module Organization

```
backend/services/canvas/
├── __init__.py              # Module initialization, exports canvas_bp
├── canvas.py                # Main Canvas blueprint with routes and functions
├── node_canvas_flows.py     # Flow management utilities (dependency graph, topological sort)
└── README.md                # This file
```

## Import Paths

### Correct Imports

```python
# Canvas service (from __init__.py)
from backend.services.canvas import canvas_bp

# Canvas blueprint directly
from backend.services.canvas.canvas import canvas_bp

# Canvas functions
from backend.services.canvas.canvas import (
    generate_mock_results,
    validate_flow,
    health_check,
    prepare_generation,
    preview_sql_results
)

# Node canvas flows utilities
from backend.services.canvas import node_canvas_flows
from backend.services.canvas.node_canvas_flows import (
    build_dependency_graph,
    topological_sort
)
```

### Incorrect Imports (DO NOT USE)

```python
# ❌ WRONG - backend.services.node does not exist
from backend.services.node import event_node_builder_bp
from backend.services.node.canvas_validation import canvas_validation_bp
from backend.services.node.canvas import canvas_bp

# ❌ WRONG - canvas_service.py doesn't exist (it's canvas.py)
from backend.services.canvas.canvas_service import canvas_bp
```

## API Endpoints

The Canvas blueprint (`canvas_bp`) provides the following routes:

### Pages

- `GET /canvas/node_canvas` - Main Canvas page (Jinja2 template)
- `GET /canvas/node_canvas_react` - Canvas page with React shell

### API Routes

- `GET /api/canvas/health` - Health check endpoint
- `POST /api/canvas/validate` - Validate Canvas flow configuration
- `POST /api/canvas/prepare` - Prepare HQL generation from Canvas flow
- `POST /api/canvas/preview-results` - Preview SQL query results

## Blueprint Registration

The Canvas blueprint is registered in `web_app.py`:

```python
from backend.services.canvas import canvas_bp

# Register blueprint (provides both /canvas/* and /api/canvas/* routes)
app.register_blueprint(canvas_bp)
```

**Note**: The blueprint does not have a `url_prefix` set, so it registers routes at both `/canvas/*` (pages) and `/api/canvas/*` (API endpoints).

## Key Functions

### canvas.py

#### `generate_mock_results(output_fields, limit=5)`
Generate mock query results for preview.

**Parameters:**
- `output_fields` (list): List of field definitions with name, alias, data_type
- `limit` (int): Number of rows to generate (default: 5)

**Returns:**
- `dict`: Mock results with columns, rows, row_count, execution_time_ms

#### `validate_flow()`
Validate Canvas flow configuration (POST `/api/canvas/validate`).

**Request Body:**
```json
{
  "nodes": [...],
  "connections": [...]
}
```

**Returns:**
- `dict`: Validation result with is_valid flag and errors list

#### `prepare_generation()`
Prepare HQL generation from Canvas flow (POST `/api/canvas/prepare`).

**Request Body:**
```json
{
  "flow_id": "...",
  "game_gid": 10000147,
  "output_ds": "2026-01-01"
}
```

**Returns:**
- `dict`: Prepared HQL with execution plan

#### `preview_sql_results()`
Preview SQL query results (POST `/api/canvas/preview-results`).

**Request Body:**
```json
{
  "sql": "SELECT ...",
  "limit": 10
}
```

**Returns:**
- `dict`: Query results with columns, rows, row_count

### node_canvas_flows.py

#### `build_dependency_graph(nodes, connections)`
Build dependency graph from nodes and connections.

**Parameters:**
- `nodes` (list): List of node definitions
- `connections` (list): List of connections between nodes

**Returns:**
- `dict`: Dependency graph with dependencies and dependents for each node

#### `topological_sort(graph)`
Perform topological sort on dependency graph.

**Parameters:**
- `graph` (dict): Dependency graph from build_dependency_graph()

**Returns:**
- `list`: Sorted list of node IDs in execution order

**Raises:**
- `ValueError`: If circular dependency is detected

## Event Nodes Integration

The Canvas system integrates with the Event Nodes service for managing event node configurations:

```python
# Event nodes are managed by a separate blueprint
from backend.services.events.event_nodes import event_nodes_bp

# Event nodes API routes:
# - GET    /api/event-nodes          - List all event nodes
# - GET    /api/event-nodes/<id>     - Get single event node
# - POST   /api/event-nodes          - Create event node
# - PUT    /api/event-nodes/<id>     - Update event node
# - DELETE /api/event-nodes/<id>     - Delete event node
```

## Migration History

### 2026-02-10: Import Path Fix

**Issue:** ModuleNotFoundError for `backend.services.node`

**Root Cause:** Code was importing from `backend.services.node` which doesn't exist. The actual Canvas module is at `backend.services.canvas`.

**Fix:** Updated all imports across the codebase:
- `web_app.py`: Removed non-existent `event_node_builder_bp` and `canvas_validation_bp`
- `manual_functional_test.py`: Changed to import `event_nodes_bp` from correct path
- `test/unit/backend/test_canvas_processor.py`: Updated all imports from `backend.services.node.canvas` to `backend.services.canvas.canvas`
- `test/unit/backend/conftest.py`: Removed non-existent blueprint import

**Files Modified:**
1. `/Users/mckenzie/Documents/event2table/web_app.py`
2. `/Users/mckenzie/Documents/event2table/manual_functional_test.py`
3. `/Users/mckenzie/Documents/event2table/test/unit/backend/test_canvas_processor.py`
4. `/Users/mckenzie/Documents/event2table/test/unit/backend/conftest.py`

**Verification:** All tests pass in `/Users/mckenzie/Documents/event2table/test/canvas_import_fix.py`

## Usage Example

### Basic Canvas Page Render

```python
from flask import Flask, render_template
from backend.services.canvas import canvas_bp

app = Flask(__name__)
app.register_blueprint(canvas_bp)

# Canvas page available at:
# http://localhost:5001/canvas/node_canvas?game_gid=10000147
```

### API Usage with Python Requests

```python
import requests

# Validate Canvas flow
response = requests.post('http://localhost:5001/api/canvas/validate', json={
    'nodes': [
        {'id': 'n1', 'type': 'event_source', 'event_id': 1},
        {'id': 'n2', 'type': 'output', 'output_name': 'test_output'}
    ],
    'connections': [
        {'source': 'n1', 'target': 'n2'}
    ]
})
validation_result = response.json()

# Prepare HQL generation
response = requests.post('http://localhost:5001/api/canvas/prepare', json={
    'flow_id': 'flow_123',
    'game_gid': 10000147,
    'output_ds': '2026-01-01'
})
hql_result = response.json()
```

## Testing

Run the Canvas import verification test:

```bash
python3 test/canvas_import_fix.py
```

Expected output:
```
✅ ALL TESTS PASSED!
Canvas module imports are working correctly.
The import path fix was successful.
```

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'backend.services.node'

**Solution:** Update your imports to use the correct path:
```python
# Instead of:
from backend.services.node import event_node_builder_bp

# Use:
from backend.services.events import event_nodes_bp
from backend.services.canvas import canvas_bp
```

### Issue: Canvas blueprint not found

**Solution:** Ensure you're importing from the correct module:
```python
# Correct:
from backend.services.canvas import canvas_bp

# Incorrect:
from backend.services.canvas.canvas_service import canvas_bp  # canvas_service.py doesn't exist
```

## Related Documentation

- [Canvas API Documentation](./CANVAS_API.md) - Detailed API endpoint documentation
- [Event Nodes Documentation](../events/EVENT_NODES.md) - Event nodes management
- [Flow Management Guide](../flows/FLOW_MANAGEMENT.md) - Canvas flow management
- [HQL Generation Guide](../hql/HQL_GENERATION.md) - HQL generation from Canvas flows

## Support

For issues or questions about the Canvas module:
1. Check this documentation
2. Run the verification test: `python3 test/canvas_import_fix.py`
3. Check logs in `backend/core/config/logs/dwd_generator.log`
4. Review the functional test report: `FUNCTIONAL_TEST_REPORT.md`

---

**Last Updated:** 2026-02-10
**Author:** Claude Code
**Version:** 1.0.0
