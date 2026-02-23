# HQL Generator Quick Reference Guide

## TL;DR

The HQL Generator produces **SELECT statements**, not CREATE VIEW statements.

## Quick Start

```python
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Event, Field

# Create generator
generator = HQLGenerator()

# Define event
event = Event(
    name="login",
    table_name="ieu_ods.ods_10000147_all_view",
    alias="e1"  # Optional, for JOIN/UNION
)

# Define fields
fields = [
    Field(name="role_id", type="base"),  # Direct column
    Field(name="zone_id", type="param", json_path="$.zoneId")  # JSON extraction
]

# Generate HQL
hql = generator.generate(
    events=[event],
    fields=fields,
    conditions=[],
    mode="single"  # or "join" or "union"
)

print(hql)
```

## Output Format

### What You Get:
```sql
SELECT
  `role_id`,
  get_json_object(params, '$.zoneId') AS `zone_id`
FROM ieu_ods.ods_10000147_all_view
WHERE
  ds = '${ds}'
```

### What You DON'T Get:
- ❌ CREATE VIEW
- ❌ CREATE TABLE
- ❌ INSERT OVERWRITE

## Three Modes

### 1. Single Mode
```python
hql = generator.generate(
    events=[event],
    fields=fields,
    conditions=[],
    mode="single"
)
```

### 2. Join Mode
```python
hql = generator.generate(
    events=[event_a, event_b],
    fields=fields,
    conditions=[],
    mode="join",
    join_config={
        "type": "INNER",  # INNER/LEFT/RIGHT/CROSS
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

### 3. Union Mode
```python
hql = generator.generate(
    events=[event_a, event_b],
    fields=fields,
    conditions=[],
    mode="union",
    use_aliases=True
)
```

## Field Types

### Base (Direct Column)
```python
Field(name="role_id", type="base")
```
Output: `role_id`

### Param (JSON Extraction)
```python
Field(name="zone_id", type="param", json_path="$.zoneId")
```
Output: `get_json_object(params, '$.zoneId') AS zone_id`

### Custom (Expression)
```python
Field(name="ts", type="custom", custom_expression="FROM_UNIXTIME(timestamp/1000)")
```
Output: `FROM_UNIXTIME(timestamp/1000) AS ts`

### Fixed (Constant)
```python
Field(name="game_id", type="fixed", fixed_value="90000001")
```
Output: `'90000001' AS game_id`

## Event Model

```python
@dataclass
class Event:
    name: str                          # Required: Event name
    table_name: str                    # Required: Full table name
    alias: Optional[str] = None        # Optional: Table alias for JOIN/UNION
    partition_field: str = "ds"        # Optional: Partition field (default: ds)
```

## Common Use Cases

### Create View
```sql
CREATE OR REPLACE VIEW dwd_event_login AS
{generated_hql}
```

### Insert Overwrite
```sql
INSERT OVERWRITE TABLE dwd.v_dwd_event_login_di
PARTITION (ds='${bizdate}')
{generated_hql}
```

### Ad-hoc Query
```bash
hive -e "{generated_hql}"
```

## Troubleshooting

### Error: "got an unexpected keyword argument 'alias'"

**Problem**: Using old Event model without alias field

**Solution**: Update to latest Event model (v2.0+)

### Error: "str object has no attribute 'get'"

**Problem**: join_config conditions is wrong format

**Wrong**:
```python
"conditions": ["a.role_id = b.role_id"]
```

**Correct**:
```python
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

## Testing

```python
# Quick test
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Event, Field

generator = HQLGenerator()
event = Event(name="login", table_name="ods.table")
fields = [Field(name="role_id", type="base")]

hql = generator.generate(events=[event], fields=fields, conditions=[], mode="single")

assert "SELECT" in hql
assert "FROM" in hql
print("✅ Test passed")
```

## Files

- **Generator**: `/Users/mckenzie/Documents/event2table/backend/services/hql/core/generator.py`
- **Models**: `/Users/mckenzie/Documents/event2table/backend/services/hql/models/event.py`
- **Documentation**: `/Users/mckenzie/Documents/event2table/docs/hql/HQL_GENERATOR_OUTPUT_FORMAT.md`
- **Tests**: `/Users/mckenzie/Documents/event2table/test_hql_generator_verification.py`

## Version

- **v2.0** (2025-02-10): Added `alias` field support
- **v1.0**: Initial release

---

**Need More Info?** See:
- [HQL_GENERATOR_OUTPUT_FORMAT.md](./HQL_GENERATOR_OUTPUT_FORMAT.md) - Complete documentation
- [HQL_GENERATOR_INVESTIGATION_REPORT.md](./HQL_GENERATOR_INVESTIGATION_REPORT.md) - Investigation details
