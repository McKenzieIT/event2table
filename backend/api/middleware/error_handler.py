"""
Unified API Error Handling & Response Format Middleware

Standard Response Format:
    Success: {"success": True, "data": ..., "message": ..., "timestamp": ...}
    Error:   {"success": False, "error": ..., "timestamp": ...}

Recommended Usage:
    from backend.core.utils import json_success_response, json_error_response

    # Success response (returns Flask jsonify tuple)
    return json_success_response(data=games, message="Games retrieved")

    # Error response (returns Flask jsonify tuple)
    return json_error_response("Not found", status_code=404)

Deprecated Patterns (DO NOT USE):
    # ❌ jsonify(success_response(data=...)[0])  -- double wrapping, loses status code
    # ❌ jsonify({"success": True, "data": ...})  -- no timestamp, inconsistent
    # ❌ success_response(data=...)               -- returns tuple, not Flask response
    # ❌ create_success_response(data=...)         -- no timestamp, not jsonified

Migration Guide:
    OLD: return jsonify(success_response(data=result)[0])
    NEW: return json_success_response(data=result)

    OLD: return jsonify(error_response(msg, status_code=400)[0]), 400
    NEW: return json_error_response(msg, status_code=400)

    OLD: return jsonify({"success": True, "data": data})
    NEW: return json_success_response(data=data)
"""

from functools import wraps
from flask import jsonify
from typing import Tuple, Dict, Any
import logging

from backend.core.utils import json_success_response, json_error_response

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


def handle_api_errors(f):
    """
    Unified API error handling decorator.

    Maps exception types to standard JSON error responses:
    - ValueError → 400 Bad Request
    - KeyError → 400 Bad Request
    - PermissionError → 403 Forbidden
    - NotFoundError → 404 Not Found
    - Exception → 500 Internal Server Error
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error in {f.__name__}: {e}")
            return json_error_response(str(e), status_code=400)
        except KeyError as e:
            logger.warning(f"Missing key in {f.__name__}: {e}")
            return json_error_response(f"Missing required field: {e}", status_code=400)
        except PermissionError as e:
            logger.warning(f"Permission denied in {f.__name__}: {e}")
            return json_error_response(str(e), status_code=403)
        except NotFoundError as e:
            logger.info(f"Resource not found in {f.__name__}: {e}")
            return json_error_response(str(e), status_code=404)
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}", exc_info=True)
            return json_error_response("An internal error occurred", status_code=500)

    return decorated_function


def create_error_response(
    message: str, status_code: int = 400
) -> Tuple[Dict[str, Any], int]:
    """Deprecated: Use json_error_response() from backend.core.utils instead."""
    return {"success": False, "error": message}, status_code


def create_success_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """Deprecated: Use json_success_response() from backend.core.utils instead."""
    response = {"success": True}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return response
