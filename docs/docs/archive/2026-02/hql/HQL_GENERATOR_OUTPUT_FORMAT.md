# HQL Generator Output Format Documentation

## Overview

The HQL Generator in event2table produces **SELECT statements** for data extraction and transformation. It is designed to be a flexible, framework-independent core component that can be used in various data pipeline scenarios.

## Important Clarification

**The HQL Generator does NOT produce CREATE VIEW or CREATE TABLE statements.**

The generator produces **SELECT queries** that can be:
- Used directly in ad-hoc queries
- Wrapped in CREATE VIEW statements
- Used in INSERT OVERWRITE operations
- Embedded in stored procedures

## Output Format

### Single Event Mode

**Purpose**: Extract data from a single event source

**Output Format**:
```sql
-- Event Node: {event_name}
-- 中文: {event_name}
SELECT
  {field1},
  {field2},
  get_json_object(params, '$.json_path') AS {param_field}
FROM {table_name}
WHERE
  ds = '${ds}'
```

**Example**:
```sql
-- Event Node: login
-- 中文: login
SELECT
  `role_id`,
  `account_id`,
  get_json_object(params, '$.zoneId') AS `zone_id`
FROM ieu_ods.ods_10000147_all_view
WHERE
  ds = '${ds}'
```

### Join Mode

**Purpose**: Join multiple event sources

**Output Format**:
```sql
-- Event Node: {event_name}
-- 中文: {event_name}
SELECT
  {event_alias1}.{field1},
  {event_alias1}.{field2}
FROM {table1} AS {event_alias1}
INNER JOIN {table2} AS {event_alias2} ON {join_conditions}
WHERE
  ds = '${ds}'
```

**Example**:
```sql
-- Event Node: login_a
-- 中文: login_a
SELECT
  login_a.role_id,
  login_a.zone_id
FROM ieu_ods.ods_10000147_all_view AS login_a
INNER JOIN ieu_ods.ods_10000148_all_view AS login_b ON login_a.role_id = login_b.role_id
WHERE
  ds = '${ds}'
```

### Union Mode

**Purpose**: Union multiple event sources (same schema)

**Output Format**:
```sql
SELECT {fields} FROM {table1} WHERE ds = '${ds}'
UNION ALL
SELECT {fields} FROM {table2} WHERE ds = '${ds}'
```

## Modes

### 1. Single Mode
- **Input**: Single Event object
- **Output**: SELECT query with field extraction
- **Use Case**: Extract fields from one event source
- **Alias**: Optional (not used in output)

### 2. Join Mode
- **Input**: Multiple Event objects + join_config
- **Output**: SELECT query with JOIN clause
- **Use Case**: Combine data from multiple events
- **Alias**: Required (used for table references)
- **join_config format**:
  ```python
  {
      "type": "INNER",  # INNER/LEFT/RIGHT/CROSS
      "conditions": [
          {
              "left_event": "event_a_name",
              "left_field": "role_id",
              "right_event": "event_b_name",
              "right_field": "role_id",
              "operator": "="
          }
      ],
      "use_aliases": True
  }
  ```

### 3. Union Mode
- **Input**: Multiple Event objects
- **Output**: UNION ALL of multiple SELECT queries
- **Use Case**: Combine similar events from different sources
- **Alias**: Optional (used for clarity if needed)

## Usage Examples

### Basic Usage

```python
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Event, Field

# Initialize generator
generator = HQLGenerator()

# Define event
event = Event(
    name="login",
    table_name="ieu_ods.ods_10000147_all_view"
)

# Define fields
fields = [
    Field(name="role_id", type="base"),
    Field(name="zone_id", type="param", json_path="$.zoneId")
]

# Generate HQL
hql = generator.generate(
    events=[event],
    fields=fields,
    conditions=[],
    mode="single"
)

print(hql)
```

### With Table Alias (for JOIN/UNION)

```python
# Define events with aliases
event_a = Event(
    name="login_a",
    table_name="ieu_ods.ods_10000147_all_view",
    alias="a"  # Optional alias
)

event_b = Event(
    name="login_b",
    table_name="ieu_ods.ods_10000148_all_view",
    alias="b"
)

# Generate JOIN HQL
hql = generator.generate(
    events=[event_a, event_b],
    fields=fields,
    conditions=[],
    mode="join",
    join_config={
        "type": "INNER",
        "conditions": [
            {
                "left_event": "login_a",
                "left_field": "role_id",
                "right_event": "login_b",
                "right_field": "role_id",
                "operator": "="
            }
        ],
        "use_aliases": True
    }
)
```

## Field Types

### 1. Base Fields (type="base")
Direct column references from the source table.

```python
Field(name="role_id", type="base")
```

**Output**: `role_id`

### 2. Param Fields (type="param")
Extract fields from JSON params column.

```python
Field(name="zone_id", type="param", json_path="$.zoneId")
```

**Output**: `get_json_object(params, '$.zoneId') AS zone_id`

### 3. Custom Fields (type="custom")
Custom HQL expressions.

```python
Field(
    name="event_timestamp",
    type="custom",
    custom_expression="FROM_UNIXTIME(timestamp/1000)"
)
```

**Output**: `FROM_UNIXTIME(timestamp/1000) AS event_timestamp`

### 4. Fixed Fields (type="fixed")
Constant values.

```python
Field(name="game_id", type="fixed", fixed_value="90000001")
```

**Output**: `'90000001' AS game_id`

## Event Model

```python
@dataclass
class Event:
    """
    Abstract event model for HQL generation

    Attributes:
        name: Event name (e.g., 'login', 'purchase')
        table_name: Full table name (e.g., 'ieu_ods.ods_10000147_all_view')
        alias: Optional table alias for JOIN/UNION operations
        partition_field: Partition field name (default: 'ds')
    """
    name: str
    table_name: str
    alias: Optional[str] = None
    partition_field: str = "ds"
```

## Field Model

```python
@dataclass
class Field:
    """
    Abstract field model for HQL generation

    Attributes:
        name: Field name
        type: Field type (base/param/custom/fixed)
        alias: Optional field alias
        json_path: JSON path for param type
        custom_expression: Custom expression for custom type
        fixed_value: Fixed value for fixed type
    """
    name: str
    type: str
    alias: Optional[str] = None
    json_path: Optional[str] = None
    custom_expression: Optional[str] = None
    fixed_value: Any = None
```

## Common Use Cases

### 1. Ad-hoc Data Extraction

Use the generated SELECT query directly for data analysis.

```python
hql = generator.generate(...)
# Execute: hive -e "{hql}"
```

### 2. Create View

Wrap the SELECT query in a CREATE VIEW statement.

```sql
CREATE OR REPLACE VIEW dwd_event_login AS
{generated_hql}
```

### 3. Insert Overwrite

Use the SELECT query to populate a table.

```sql
INSERT OVERWRITE TABLE dwd.v_dwd_event_login_di
PARTITION (ds='${bizdate}')
{generated_hql}
```

### 4. Scheduled Pipeline

Embed in a scheduled data pipeline script.

```bash
#!/bin/bash
BIZDATE=$(date -d "yesterday" +%Y%m%d)
HQL=$(python generate_hql.py ...)
hive -e "SET hivevar:ds=${BIZDATE}; ${HQL}"
```

## Integration Examples

### Flask API Integration

```python
from flask import jsonify
from backend.services.hql.core.generator import HQLGenerator

@app.route('/api/hql/preview', methods=['POST'])
def preview_hql():
    data = request.json

    generator = HQLGenerator()
    event = Event(**data['event'])
    fields = [Field(**f) for f in data['fields']]

    hql = generator.generate(
        events=[event],
        fields=fields,
        conditions=[],
        mode="single"
    )

    return jsonify({"hql": hql})
```

### Canvas Integration

```python
# In canvas preview component
def generate_live_preview(event_nodes, field_configs):
    generator = HQLGenerator()

    events = [Event(
        name=node['name'],
        table_name=node['table_name'],
        alias=node.get('alias')
    ) for node in event_nodes]

    fields = [Field(**fc) for fc in field_configs]

    hql = generator.generate(
        events=events,
        fields=fields,
        conditions=[],
        mode="join" if len(events) > 1 else "single",
        join_config=canvas_config.get('join_config')
    )

    return hql
```

## Testing

### Test Single Mode

```python
def test_single_mode():
    from backend.services.hql.core.generator import HQLGenerator
    from backend.services.hql.models.event import Event, Field

    generator = HQLGenerator()
    event = Event(name="login", table_name="ods.table")
    fields = [Field(name="role_id", type="base")]

    hql = generator.generate(
        events=[event],
        fields=fields,
        conditions=[],
        mode="single"
    )

    assert "SELECT" in hql
    assert "FROM" in hql
    assert "role_id" in hql
    print("✅ Single mode test passed")
```

### Test Join Mode

```python
def test_join_mode():
    from backend.services.hql.core.generator import HQLGenerator
    from backend.services.hql.models.event import Event, Field

    generator = HQLGenerator()

    event_a = Event(name="login_a", table_name="ods.table_a", alias="a")
    event_b = Event(name="login_b", table_name="ods.table_b", alias="b")
    fields = [Field(name="role_id", type="base")]

    hql = generator.generate(
        events=[event_a, event_b],
        fields=fields,
        conditions=[],
        mode="join",
        join_config={
            "type": "INNER",
            "conditions": [
                {
                    "left_event": "login_a",
                    "left_field": "role_id",
                    "right_event": "login_b",
                    "right_field": "role_id",
                    "operator": "="
                }
            ],
            "use_aliases": True
        }
    )

    assert "JOIN" in hql
    assert "login_a.role_id" in hql
    print("✅ Join mode test passed")
```

## Troubleshooting

### Issue: "got an unexpected keyword argument 'alias'"

**Solution**: Ensure you're using the updated Event model with the `alias` field.

```python
# Correct
event = Event(
    name="login",
    table_name="ods.table",
    alias="e1"  # Now supported!
)
```

### Issue: Join mode fails with "str object has no attribute 'get'"

**Solution**: Ensure join_config conditions are dictionaries, not strings.

```python
# Incorrect
"conditions": ["a.role_id = b.role_id"]

# Correct
"conditions": [
    {
        "left_event": "login_a",
        "left_field": "role_id",
        "right_event": "login_b",
        "right_field": "role_id",
        "operator": "="
    }
]
```

## Best Practices

1. **Always validate input**: Check that Event and Field objects are valid before generation
2. **Use aliases in join mode**: Prevents ambiguity when joining tables with same columns
3. **Test generated HQL**: Execute in test environment before production
4. **Handle partition filters**: Always include partition conditions to prevent full table scans
5. **Document field mappings**: Keep track of which fields come from which events

## Version History

- **v2.0** (2025-02-10): Added `alias` field to Event model for JOIN/UNION support
- **v1.0**: Initial release with basic HQL generation

## Related Files

- `/Users/mckenzie/Documents/event2table/backend/services/hql/core/generator.py` - Core generator
- `/Users/mckenzie/Documents/event2table/backend/services/hql/models/event.py` - Data models
- `/Users/mckenzie/Documents/event2table/backend/services/hql/builders/` - HQL builders
- `/Users/mckenzie/Documents/event2table/test_hql_generator_verification.py` - Test suite
