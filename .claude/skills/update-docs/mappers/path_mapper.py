"""
Path-based Mapper.

Maps files to documentation based on path patterns.
"""
from typing import List, Dict, Any


class PathMapper:
    """Maps files using path-based rules."""

    PATH_RULES = {
        "backend/api/routes/": {
            "target": "docs/api/",
            "action": "update_endpoint",
            "doc_type": "api"
        },
        "backend/services/": {
            "target": "docs/development/backend-development.md",
            "action": "update_service",
            "doc_type": "guide"
        },
        "backend/models/repositories/": {
            "target": "docs/development/backend-development.md",
            "action": "update_repository",
            "doc_type": "guide"
        },
        "frontend/src/features/": {
            "target": "docs/development/frontend-development.md",
            "action": "update_feature",
            "doc_type": "guide"
        },
        "backend/services/hql/": {
            "target": "docs/hql/",
            "action": "update_hql",
            "doc_type": "technical"
        },
    }

    def map(self, file_path: str) -> List[Dict[str, Any]]:
        """Map a file path to target documentation."""
        normalized_path = file_path.replace("\\", "/")
        results = []

        for pattern, rule in self.PATH_RULES.items():
            if pattern in normalized_path:
                result = {
                    "target": rule["target"],
                    "action": rule["action"],
                    "doc_type": rule["doc_type"],
                    "source": file_path
                }
                results.append(result)

        return results if results else []
