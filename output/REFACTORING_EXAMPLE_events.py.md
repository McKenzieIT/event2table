# Backend Error Handling Refactoring Example

## File: backend/api/routes/events.py

### BEFORE (Lines 101-113) - 13 lines
```python
try:
    # Use EventService for paginated list with caching
    result = event_service.get_events_paginated(
        game_gid=game_gid, page=page, per_page=per_page, search=search if search else None
    )

    return json_success_response(data=result)

except ValueError as e:
    return json_error_response(str(e), status_code=400)
except Exception as e:
    logger.error(f"Error listing events: {e}")
    return json_error_response("Failed to list events", status_code=500)
```

### AFTER (Lines 101-107) - 7 lines
```python
# Use EventService for paginated list with caching
result = event_service.get_events_paginated(
    game_gid=game_gid, page=page, per_page=per_page, search=search if search else None
)

return json_success_response(data=result)
```

### Full Refactored Endpoint (With Decorator)
```python
from backend.core.utils.common import handle_api_errors

@api_bp.route("/api/events", methods=["GET"])
@handle_api_errors("Failed to list events")
def api_list_events() -> Tuple[Dict[str, Any], int]:
    """
    API: List all events with pagination support and search

    Query Parameters:
        - game_gid: Filter by game GID (optional)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - search: Search keyword for event names (optional)

    Returns:
        Tuple containing response dictionary and HTTP status code

    Response Format:
        {
            "success": true,
            "data": {
                "events": [...],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 100,
                    "total_pages": 5
                }
            }
        }
    """
    game_gid_str = request.args.get("game_gid")
    game_gid = safe_int_convert(game_gid_str) if game_gid_str else None

    logger.info(f"API: game_gid_str={game_gid_str}, game_gid={game_gid}, type={type(game_gid)}")

    page = safe_int_convert(request.args.get("page"), 1, 1)
    per_page = safe_int_convert(request.args.get("per_page"), 20, 1)
    search = request.args.get("search", "").strip()

    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    if per_page > 100:
        per_page = 100

    # Use EventService for paginated list with caching
    result = event_service.get_events_paginated(
        game_gid=game_gid, page=page, per_page=per_page, search=search if search else None
    )

    return json_success_response(data=result)
```

### Benefits
- **Lines reduced**: 13 → 7 (46% reduction)
- **Error handling**: Centralized and consistent
- **Logging**: Automatic error logging
- **Maintainability**: Easier to add new endpoints

### Before (Create Event - Lines 117-210) - 94 lines
```python
@api_bp.route("/api/events", methods=["POST"])
def api_create_event():
    """API: Create a new event"""
    try:
        is_valid, data, error = validate_json_request(["game_gid", "event_name", "event_name_cn"])
        if not is_valid:
            return json_error_response(error, status_code=400)

        # 验证游戏GID
        is_valid_game, game_error = validate_game_gid(data["game_gid"])
        if not is_valid_game:
            return json_error_response(game_error, status_code=400)

        # Validate input lengths
        event_name = data.get("event_name", "").strip()
        event_name_cn = data.get("event_name_cn", "").strip()

        if len(event_name) == 0:
            return json_error_response("event_name cannot be empty", status_code=400)
        if len(event_name) > 200:
            return json_error_response(
                "event_name exceeds maximum length of 200 characters", status_code=400
            )
        if len(event_name_cn) > 200:
            return json_error_response(
                "event_name_cn exceeds maximum length of 200 characters",
                status_code=400,
            )

        # Sanitize input
        event_name = html.escape(event_name)
        event_name_cn = html.escape(event_name_cn)

        # Handle category_id
        category_id = data.get("category_id")
        if not category_id or (isinstance(category_id, str) and category_id.strip() == ""):
            category_id = None

        # Validate or create default category
        if category_id:
            if not event_service.validate_category_exists(category_id):
                return json_error_response(
                    f"Category with id {category_id} not found", status_code=400
                )
        else:
            category_id = event_service.get_or_create_default_category()

        # Prepare parameters list
        param_names = data.get("param_names", [])
        param_names_cn = data.get("param_names_cn", [])
        param_types = data.get("param_types", [])
        param_descriptions = data.get("param_descriptions", [])

        parameters = []
        for i, name in enumerate(param_names):
            if name:
                parameters.append(
                    {
                        "param_name": name,
                        "param_name_cn": param_names_cn[i] if i < len(param_names_cn) else "",
                        "template_id": param_types[i] if i < len(param_types) else 1,
                        "param_description": (
                            param_descriptions[i] if i < len(param_descriptions) else ""
                        ),
                    }
                )

        # Create EventEntity
        from backend.models.entities import EventEntity

        event_data = EventEntity(
            game_gid=data["game_gid"],
            name=event_name,
            name_cn=event_name_cn,
            category_id=category_id,
            include_in_common_params=data.get("include_in_common_params", 1),
        )

        # Use EventService to create event with parameters
        event = event_service.create_event_with_parameters(event_data, parameters)

        logger.info(f"Event created: {event_name} (ID: {event.id})")
        return json_success_response(
            data={"event_id": event.id}, message="Event created successfully"
        )

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return json_error_response("Failed to create event", status_code=500)
```

### After (Create Event) - 80 lines
```python
from backend.core.utils.common import (
    handle_api_errors,
    sanitize_string,
    validate_request_json,
)

@api_bp.route("/api/events", methods=["POST"])
@handle_api_errors(
    error_message="Failed to create event",
    validation_error_message="Event validation failed"
)
def api_create_event():
    """API: Create a new event"""
    # Validate request JSON (raises ValueError if invalid)
    data = validate_request_json(required_fields=["game_gid", "event_name", "event_name_cn"])

    # 验证游戏GID
    is_valid_game, game_error = validate_game_gid(data["game_gid"])
    if not is_valid_game:
        return json_error_response(game_error, status_code=400)

    # Sanitize and validate input lengths
    event_name = sanitize_string(data.get("event_name", ""))
    event_name_cn = sanitize_string(data.get("event_name_cn", ""))

    if not event_name:
        raise ValueError("event_name cannot be empty")
    if len(event_name) > 200:
        raise ValueError("event_name exceeds maximum length of 200 characters")
    if len(event_name_cn) > 200:
        raise ValueError("event_name_cn exceeds maximum length of 200 characters")

    # Handle category_id
    category_id = data.get("category_id")
    if not category_id or (isinstance(category_id, str) and category_id.strip() == ""):
        category_id = None

    # Validate or create default category
    if category_id:
        if not event_service.validate_category_exists(category_id):
            raise ValueError(f"Category with id {category_id} not found")
    else:
        category_id = event_service.get_or_create_default_category()

    # Prepare parameters list
    param_names = data.get("param_names", [])
    param_names_cn = data.get("param_names_cn", [])
    param_types = data.get("param_types", [])
    param_descriptions = data.get("param_descriptions", [])

    parameters = []
    for i, name in enumerate(param_names):
        if name:
            parameters.append(
                {
                    "param_name": name,
                    "param_name_cn": param_names_cn[i] if i < len(param_names_cn) else "",
                    "template_id": param_types[i] if i < len(param_types) else 1,
                    "param_description": (
                        param_descriptions[i] if i < len(param_descriptions) else ""
                    ),
                }
            )

    # Create EventEntity
    from backend.models.entities import EventEntity

    event_data = EventEntity(
        game_gid=data["game_gid"],
        name=event_name,
        name_cn=event_name_cn,
        category_id=category_id,
        include_in_common_params=data.get("include_in_common_params", 1),
    )

    # Use EventService to create event with parameters
    event = event_service.create_event_with_parameters(event_data, parameters)

    logger.info(f"Event created: {event_name} (ID: {event.id})")
    return json_success_response(
        data={"event_id": event.id}, message="Event created successfully"
    )
```

### Benefits
- **Lines reduced**: 94 → 80 (15% reduction)
- **Sanitization**: Using shared `sanitize_string()` utility
- **Error handling**: Automatic ValidationError and Exception handling
- **Consistency**: All errors follow same pattern

## Implementation Plan

### Files to Refactor
1. ✅ `backend/api/routes/events.py` (Example above)
2. `backend/api/routes/games.py`
3. `backend/api/routes/categories.py`
4. `backend/api/routes/parameters.py`
5. `backend/api/routes/flows.py`

### Step-by-Step Process
1. Add import: `from backend.core.utils.common import handle_api_errors, sanitize_string, validate_request_json`
2. Remove try-except blocks
3. Add `@handle_api_errors()` decorator
4. Replace `html.escape()` with `sanitize_string()`
5. Replace `validate_json_request()` with `validate_request_json()` (raises ValueError)
6. Test each endpoint

### Testing
```bash
# Test events API
pytest backend/test/unit/api/test_events_api.py -v

# Manual testing
curl http://127.0.0.1:5001/api/events
curl -X POST http://127.0.0.1:5001/api/events -H "Content-Type: application/json" -d '{"game_gid": 90000001, "event_name": "test", "event_name_cn": "测试"}'
```

---

**Status**: Example created, ready to apply to all endpoints
**Estimated Time**: 30 minutes for all 5 files
**Impact**: ~300 lines of code reduction across backend
