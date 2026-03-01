# CanvasService API Quick Reference

**Version**: 1.0.0
**Last Updated**: 2026-03-01

---

## Initialization

```python
from backend.services.canvas.canvas_service import CanvasService, get_canvas_service

# Option 1: Direct instantiation
service = CanvasService()

# Option 2: Singleton pattern (recommended)
service = get_canvas_service()
```

---

## Flow Template Operations

### Create Flow

```python
flow = service.create_flow(
    game_gid=10000147,           # Required
    flow_name="Login Flow",      # Required
    flow_graph={                 # Required
        "nodes": [
            {"id": "n1", "type": "event_source", "data": {"event_id": 1}},
            {"id": "n2", "type": "output", "data": {"name": "Output"}}
        ],
        "connections": [
            {"source": "n1", "target": "n2"}
        ]
    },
    variables={"key": "value"},  # Optional
    description="User login flow",  # Optional
    created_by="admin"           # Optional
)

# Returns: FlowEntity
print(f"Flow created: ID={flow.id}, Name={flow.flow_name}")
```

### Get Flow by ID

```python
flow = service.get_flow(flow_id=1)

# Returns: FlowEntity or None
if flow:
    print(f"Flow: {flow.flow_name}")
    print(f"Nodes: {len(flow.flow_graph['nodes'])}")
```

### Get Flows by Game

```python
flows = service.get_flows_by_game(game_gid=10000147)

# Returns: List[FlowEntity]
print(f"Found {len(flows)} flows")
for flow in flows:
    print(f" - {flow.flow_name}")
```

### Get All Flows

```python
flows = service.get_all_flows()

# Returns: List[FlowEntity]
```

### Update Flow

```python
success = service.update_flow(
    flow_id=1,
    flow_name="Updated Name",           # Optional
    flow_graph={"nodes": [], ...},      # Optional
    variables={"new_key": "value"},     # Optional
    description="Updated description",  # Optional
    is_active=True                      # Optional
)

# Returns: bool
print(f"Update {'succeeded' if success else 'failed'}")
```

### Delete Flow (Soft Delete)

```python
success = service.delete_flow(
    flow_id=1,
    game_gid=10000147  # Required for cache invalidation
)

# Returns: bool
```

### Export Flow Config

```python
config = service.export_flow_config(flow_id=1)

# Returns: dict or None
if config:
    print(f"Flow: {config['flow']['flow_name']}")
    print(f"Exported: {config['exported_at']}")
```

### Export Flow HQL Metadata

```python
hql_export = service.export_flow_hql(flow_id=1)

# Returns: dict or None
if hql_export:
    print(f"Execution order: {hql_export['execution_order']}")
    print(f"Node count: {hql_export['node_count']}")
```

### Count Flows by Game

```python
count = service.count_flows_by_game(game_gid=10000147)

# Returns: int
print(f"Total flows: {count}")
```

---

## EventNode Operations

### Create EventNode

```python
node = service.create_event_node(
    game_gid=10000147,           # Required
    name="Login Node",           # Required
    event_id=1,                  # Required
    config_json={                # Required
        "fields": ["role_id", "zone_id"],
        "mode": "single",
        "where": []
    }
)

# Returns: EventNodeEntity
print(f"Node created: ID={node.id}, Name={node.name}")
```

### Get EventNode by ID

```python
node = service.get_event_node(node_id=1)

# Returns: EventNodeEntity or None
if node:
    print(f"Node: {node.name}")
    print(f"Config: {node.config_json}")
```

### Get EventNodes by Game

```python
nodes = service.get_event_nodes_by_game(game_gid=10000147)

# Returns: List[EventNodeEntity]
print(f"Found {len(nodes)} nodes")
```

### Get EventNodes by Event

```python
nodes = service.get_event_nodes_by_event(event_id=1)

# Returns: List[EventNodeEntity]
```

### Update EventNode

```python
success = service.update_event_node(
    node_id=1,
    game_gid=10000147,        # Required for cache invalidation
    event_id=1,               # Required for cache invalidation
    name="Updated Name",      # Optional
    config_json={...},        # Optional
    is_active=True            # Optional
)

# Returns: bool
```

### Delete EventNode (Soft Delete)

```python
success = service.delete_event_node(
    node_id=1,
    game_gid=10000147,  # Required for cache invalidation
    event_id=1          # Required for cache invalidation
)

# Returns: bool
```

### Count EventNodes by Game

```python
count = service.count_event_nodes_by_game(game_gid=10000147)

# Returns: int
```

---

## Flow Validation Operations

### Validate Flow Graph

```python
validation = service.validate_flow(flow_graph={
    "nodes": [...],
    "connections": [...]
})

# Returns: dict
# {
#     "valid": bool,
#     "execution_order": list or None,
#     "errors": list or None
# }

if validation["valid"]:
    print(f"✅ Valid flow")
    print(f"Execution order: {' -> '.join(validation['execution_order'])}")
else:
    print(f"❌ Invalid flow")
    for error in validation["errors"]:
        print(f"  - {error}")
```

### Prepare Flow for HQL Generation

```python
prep = service.prepare_flow_for_generation(flow_graph)

# Returns: dict
# {
#     "success": bool,
#     "execution_order": list,
#     "node_count": int,
#     "connection_count": int,
#     "error": str or None
# }

if prep["success"]:
    print(f"✅ Flow ready for generation")
    print(f"Nodes: {prep['node_count']}, Connections: {prep['connection_count']}")
else:
    print(f"❌ Preparation failed: {prep['error']}")
```

### Build Dependency Graph

```python
graph = service.build_flow_dependency_graph(
    nodes=[...],
    connections=[...]
)

# Returns: dict
# {
#     "node_id": {
#         "dependencies": [],
#         "dependents": [],
#         "node": {...}
#     }
# }

for node_id, data in graph.items():
    print(f"{node_id}: {len(data['dependencies'])} dependencies")
```

### Detect Flow Cycles

```python
cycles = service.detect_flow_cycles(
    nodes=[...],
    connections=[...]
)

# Returns: dict
# {
#     "hasCycles": bool,
#     "cycles": [[...]]
# }

if cycles["hasCycles"]:
    print(f"❌ Cycles detected!")
    for i, cycle in enumerate(cycles["cycles"]):
        print(f"  Cycle {i+1}: {' -> '.join(cycle)}")
else:
    print(f"✅ No cycles detected")
```

### Topological Sort Flow

```python
try:
    order = service.topological_sort_flow(
        nodes=[...],
        connections=[...]
    )

    # Returns: List[str] (node IDs in execution order)
    print(f"Execution order: {' -> '.join(order)}")

except ValueError as e:
    print(f"❌ Cannot sort: {e}")
```

---

## REST API Endpoints

### Flow Management

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/canvas/flows` | List flows | - | `{"flows": [...]}` |
| GET | `/api/canvas/flows?game_gid=10000147` | List flows by game | - | `{"flows": [...]}` |
| GET | `/api/canvas/flows/<id>` | Get flow | - | `{"flow": {...}}` |
| POST | `/api/canvas/flows` | Create flow | `{game_gid, flow_name, flow_graph, ...}` | `{"flow": {...}}` |
| PUT | `/api/canvas/flows/<id>` | Update flow | `{flow_name, flow_graph, ...}` | `{message}` |
| DELETE | `/api/canvas/flows/<id>?game_gid=10000147` | Delete flow | - | `{message}` |
| GET | `/api/canvas/flows/<id>/export?format=config` | Export config | - | `{flow, exported_at}` |
| GET | `/api/canvas/flows/<id>/export?format=hql` | Export HQL | - | `{flow_id, execution_order, ...}` |

### Existing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/canvas/node_canvas` | Node canvas page (Jinja) |
| GET | `/canvas/node_canvas_react` | Node canvas page (React) |
| GET | `/api/canvas/health` | Health check |
| POST | `/api/canvas/validate` | Validate flow graph |
| POST | `/api/canvas/prepare` | Prepare flow for generation |
| POST | `/api/canvas/preview-results` | Preview SQL results (mock) |

---

## Flow Graph Schema

### Nodes Array

```javascript
[
    {
        "id": "n1",                    // Required: Unique node ID
        "type": "event_source",        // Required: Node type
        "data": {                      // Required: Node data
            "event_id": 1,             // For event_source nodes
            "name": "Login Event"
        }
    },
    {
        "id": "n2",
        "type": "output",
        "data": {
            "name": "Output Table"
        }
    }
]
```

### Connections Array

```javascript
[
    {
        "source": "n1",    // Required: Source node ID
        "target": "n2"     // Required: Target node ID
    }
]
```

### Node Types

- `event_source`: Event data source node
- `join`: Join operation node
- `union`: Union operation node
- `filter`: Filter/Where condition node
- `output`: Output table node

---

## Error Handling

### ValueError

Raised when:
- Game not found
- Event not found
- Flow not found
- EventNode not found
- Invalid flow graph structure

### Example

```python
try:
    flow = service.create_flow(
        game_gid=999999,  # Invalid game
        flow_name="Test",
        flow_graph={}
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Cache Keys

The CanvasService uses the following cache keys:

- `flow:{id}` - Single flow
- `flows:game:{game_gid}` - Flows by game
- `flows:all` - All flows
- `event_node:{id}` - Single event node
- `event_nodes:game:{game_gid}` - Event nodes by game
- `event_nodes:event:{event_id}` - Event nodes by event

Cache TTL:
- L1 (in-memory): 120 seconds (2 minutes)
- L2 (Redis): 600 seconds (10 minutes)

---

## Examples

### Complete Flow Creation Workflow

```python
# 1. Initialize service
service = get_canvas_service()

# 2. Create flow graph
flow_graph = {
    "nodes": [
        {"id": "n1", "type": "event_source", "data": {"event_id": 1}},
        {"id": "n2", "type": "output", "data": {"name": "Login Output"}}
    ],
    "connections": [
        {"source": "n1", "target": "n2"}
    ]
}

# 3. Validate flow graph
validation = service.validate_flow(flow_graph)
if not validation["valid"]:
    print(f"Invalid flow: {validation['errors']}")
    exit(1)

# 4. Create flow
flow = service.create_flow(
    game_gid=10000147,
    flow_name="Login Flow",
    flow_graph=flow_graph,
    description="User login analysis"
)

print(f"Flow created: ID={flow.id}")

# 5. Export flow config
config = service.export_flow_config(flow.id)
print(f"Exported: {config['exported_at']}")

# 6. Delete flow (cleanup)
service.delete_flow(flow.id, game_gid=10000147)
print("Flow deleted")
```

---

## Best Practices

1. **Always validate flow graphs before creating flows**
   ```python
   validation = service.validate_flow(flow_graph)
   if not validation["valid"]:
       # Handle errors
       return
   ```

2. **Use game_gid parameter for cache invalidation**
   ```python
   # ✅ Correct
   service.delete_flow(flow_id, game_gid=10000147)

   # ❌ Wrong (cache not invalidated)
   service.delete_flow(flow_id, game_gid=None)
   ```

3. **Handle None returns for get operations**
   ```python
   flow = service.get_flow(flow_id)
   if flow is None:
       # Handle not found
       return {"error": "Flow not found"}, 404
   ```

4. **Use try-except for ValueError**
   ```python
   try:
       flow = service.create_flow(...)
   except ValueError as e:
       return {"error": str(e)}, 400
   ```

---

**For more details, see**: [CanvasService Implementation Report](./canvas-service-implementation.md)
