"""Event2Table Backend Package"""

import os

# Only import API modules when not in test mode
# This prevents GraphQL schema MRO conflicts during testing
if os.environ.get("FLASK_ENV") != "testing":
    try:
        from . import core
        from . import api
        from . import models
        from . import services
    except ImportError as e:
        # Log but don't fail during import
        import logging
        logging.warning(f"Failed to import backend modules: {e}")

__version__ = "1.0.0"

