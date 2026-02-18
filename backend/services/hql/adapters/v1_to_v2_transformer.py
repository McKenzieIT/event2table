"""
V1 to V2 HQL API Transformer

Converts V1 field-builder API requests to V2 HQL preview API format.

V1 Format (field-builder):
{
    "config": {
        "view_config": {...},
        "base_fields": ["ds", "role_id", ...],
        "custom_fields": {...}
    },
    "source_events": [1, 2, 3],  # event IDs
    "view_name": "v_dwd_custom_view",
    "date_var": "${bizdate}"
}

V2 Format (hql-preview-v2):
{
    "events": [{"game_gid": 10000147, "event_id": 1}],
    "fields": [{"fieldName": "role_id", "fieldType": "base"}],
    "where_conditions": [],
    "options": {"mode": "single", "include_performance": True}
}
"""

from typing import Dict, Any, List, Optional
import json


class V1ToV2Transformer:
    """
    Transformer for converting V1 field-builder requests to V2 format
    """

    # Standard base fields that should always be included
    STANDARD_BASE_FIELDS = ["ds", "role_id", "account_id", "utdid", "envinfo", "tm", "ts"]

    @staticmethod
    def transform_hql_request(v1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform V1 field-builder HQL request to V2 format

        Args:
            v1_data: V1 format request data
                {
                    "config": {
                        "view_config": {...},
                        "base_fields": [...],
                        "custom_fields": {...}
                    },
                    "source_events": [1, 2, 3],
                    "view_name": "v_dwd_custom_view",
                    "date_var": "${bizdate}"
                }

        Returns:
            V2 format request data
                {
                    "events": [{"game_gid": GID, "event_id": ID}],
                    "fields": [{"fieldName": ..., "fieldType": ...}],
                    "where_conditions": [],
                    "options": {"mode": "single", "include_performance": True}
                }

        Raises:
            ValueError: If required fields are missing or invalid
            KeyError: If config structure is invalid
        """
        # Validate required V1 fields
        if "config" not in v1_data:
            raise ValueError("Missing required field: config")

        if "source_events" not in v1_data:
            raise ValueError("Missing required field: source_events")

        config = v1_data["config"]
        source_events = v1_data["source_events"]

        if not isinstance(source_events, list) or not source_events:
            raise ValueError("source_events must be a non-empty list")

        # Extract view_config for options
        view_config = config.get("view_config", {})

        # Transform events
        events = V1ToV2Transformer.transform_events(source_events)

        # Transform fields
        base_fields = config.get("base_fields", [])
        custom_fields = config.get("custom_fields", {})
        fields = V1ToV2Transformer.transform_fields(base_fields, custom_fields)

        # Build V2 request
        v2_data = {
            "events": events,
            "fields": fields,
            "where_conditions": [],  # V1 doesn't have WHERE conditions
            "options": V1ToV2Transformer.transform_view_config(view_config),
        }

        return v2_data

    @staticmethod
    def transform_events(source_events: List[int]) -> List[Dict[str, Any]]:
        """
        Convert V1 source_events (list of IDs) to V2 events format

        Args:
            source_events: List of event IDs [1, 2, 3]

        Returns:
            List of event dicts with game_gid and event_id
            [{"game_gid": 10000147, "event_id": 1}, ...]

        Raises:
            ValueError: If event IDs are invalid
        """
        events = []

        for event_id in source_events:
            if not isinstance(event_id, int) or event_id <= 0:
                raise ValueError(f"Invalid event_id: {event_id}")

            # Note: game_gid will be looked up by ProjectAdapter.event_from_project()
            # We pass 0 as placeholder - the actual game_gid comes from database
            events.append({"game_gid": 0, "event_id": event_id})

        return events

    @staticmethod
    def transform_fields(
        base_fields: List[str], custom_fields: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Convert V1 base_fields and custom_fields to V2 fields array

        Args:
            base_fields: List of base field names ["ds", "role_id", ...]
            custom_fields: Dict of custom fields
                {
                    "role_id": {"fieldType": "base", "alias": "role"},
                    "zone_id": {"fieldType": "param", "jsonPath": "$.zoneId"},
                    "custom_expr": {"fieldType": "custom", "customExpression": "..."}
                }

        Returns:
            List of V2 field objects
            [
                {"fieldName": "ds", "fieldType": "base"},
                {"fieldName": "role_id", "fieldType": "base"},
                {"fieldName": "zone_id", "fieldType": "param", "jsonPath": "$.zoneId"},
                ...
            ]

        Raises:
            ValueError: If field configuration is invalid
        """
        fields = []

        # Process base_fields (simple list of field names)
        if base_fields:
            if not isinstance(base_fields, list):
                raise ValueError("base_fields must be a list")

            for field_name in base_fields:
                if not field_name or not isinstance(field_name, str):
                    continue

                # Check if this field has custom config
                if field_name in custom_fields:
                    # Use custom configuration
                    field_config = custom_fields[field_name]
                    field_obj = V1ToV2Transformer._build_field_object(field_name, field_config)
                    fields.append(field_obj)
                else:
                    # Default to base type
                    fields.append({"fieldName": field_name, "fieldType": "base"})

        # Process additional custom_fields not in base_fields
        if custom_fields:
            if not isinstance(custom_fields, dict):
                raise ValueError("custom_fields must be a dict")

            for field_name, field_config in custom_fields.items():
                # Skip if already processed in base_fields
                if field_name in base_fields:
                    continue

                field_obj = V1ToV2Transformer._build_field_object(field_name, field_config)
                fields.append(field_obj)

        # Ensure standard base fields are present
        for std_field in V1ToV2Transformer.STANDARD_BASE_FIELDS:
            if not any(f.get("fieldName") == std_field for f in fields):
                fields.append({"fieldName": std_field, "fieldType": "base"})

        return fields

    @staticmethod
    def _build_field_object(field_name: str, field_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a single V2 field object from V1 field config

        Args:
            field_name: Field name
            field_config: Field configuration dict
                {
                    "fieldType": "base|param|custom|fixed",
                    "alias": "optional_alias",
                    "jsonPath": "$.zoneId",  # for param type
                    "customExpression": "...",  # for custom type
                    "fixedValue": "..."  # for fixed type
                }

        Returns:
            V2 field object dict

        Raises:
            ValueError: If field config is invalid
        """
        if not isinstance(field_config, dict):
            raise ValueError(f"Invalid config for field {field_name}: must be dict")

        field_type = field_config.get("fieldType", "base")

        # Validate field type
        valid_types = ["base", "param", "custom", "fixed"]
        if field_type not in valid_types:
            raise ValueError(f"Invalid fieldType '{field_type}' for field {field_name}")

        field_obj = {"fieldName": field_name, "fieldType": field_type}

        # Add optional fields
        if "alias" in field_config:
            field_obj["alias"] = field_config["alias"]

        if "aggregateFunc" in field_config:
            field_obj["aggregateFunc"] = field_config["aggregateFunc"]

        # Type-specific fields
        if field_type == "param":
            if "jsonPath" not in field_config:
                raise ValueError(f"param field {field_name} requires jsonPath")
            field_obj["jsonPath"] = field_config["jsonPath"]

        elif field_type == "custom":
            if "customExpression" not in field_config:
                raise ValueError(f"custom field {field_name} requires customExpression")
            field_obj["customExpression"] = field_config["customExpression"]

        elif field_type == "fixed":
            if "fixedValue" not in field_config:
                raise ValueError(f"fixed field {field_name} requires fixedValue")
            field_obj["fixedValue"] = field_config["fixedValue"]

        return field_obj

    @staticmethod
    def transform_view_config(view_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract view configuration from V1 config and map to V2 options

        Args:
            view_config: V1 view_config dict
                {
                    "mode": "single|join|union",
                    "includePerformance": true,
                    "sqlMode": "VIEW|PROCEDURE",
                    ...
                }

        Returns:
            V2 options dict
                {
                    "mode": "single",
                    "include_performance": True,
                    "sql_mode": "VIEW"
                }
        """
        options = {
            "mode": view_config.get("mode", "single"),
            "include_performance": view_config.get("includePerformance", True),
            "sql_mode": view_config.get("sqlMode", "VIEW"),
        }

        # Validate mode
        valid_modes = ["single", "join", "union"]
        if options["mode"] not in valid_modes:
            options["mode"] = "single"

        # Validate sql_mode
        valid_sql_modes = ["VIEW", "PROCEDURE", "CUSTOM"]
        if options["sql_mode"] not in valid_sql_modes:
            options["sql_mode"] = "VIEW"

        return options

    @staticmethod
    def validate_v1_request(v1_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate V1 request data structure

        Args:
            v1_data: V1 format request data

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required top-level fields
            if "config" not in v1_data:
                return False, "Missing required field: config"

            if "source_events" not in v1_data:
                return False, "Missing required field: source_events"

            config = v1_data["config"]
            source_events = v1_data["source_events"]

            # Validate config
            if not isinstance(config, dict):
                return False, "config must be a dict"

            if "base_fields" in config and not isinstance(config["base_fields"], list):
                return False, "base_fields must be a list"

            if "custom_fields" in config and not isinstance(config["custom_fields"], dict):
                return False, "custom_fields must be a dict"

            # Validate source_events
            if not isinstance(source_events, list):
                return False, "source_events must be a list"

            if not source_events:
                return False, "source_events cannot be empty"

            for event_id in source_events:
                if not isinstance(event_id, int) or event_id <= 0:
                    return False, f"Invalid event_id: {event_id}"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Convenience function for backward compatibility
def transform_v1_to_v2(v1_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to transform V1 request to V2 format

    Args:
        v1_data: V1 format request data

    Returns:
        V2 format request data

    Raises:
        ValueError: If validation or transformation fails
    """
    # Validate first
    is_valid, error_msg = V1ToV2Transformer.validate_v1_request(v1_data)
    if not is_valid:
        raise ValueError(error_msg)

    # Transform
    return V1ToV2Transformer.transform_hql_request(v1_data)
