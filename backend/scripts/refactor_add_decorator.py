#!/usr/bin/env python3
"""
Script to add @handle_api_errors decorator to API routes
"""

import re
from pathlib import Path


def add_decorator_to_file(file_path: Path):
    """Add @handle_api_errors import and decorator to endpoints"""
    content = file_path.read_text()

    # Check if already imported
    if "from backend.core.utils.common import handle_api_errors" in content:
        print(f"✓ {file_path.name}: Already imports handle_api_errors")
        return False

    # Add import after existing backend.core.utils imports
    import_pattern = r"(from backend\.core\.utils import \[?[^\n]+\]?)"
    import_replacement = r"\1\nfrom backend.core.utils.common import handle_api_errors"

    if re.search(import_pattern, content):
        content = re.sub(import_pattern, import_replacement, content, count=1)
        print(f"✓ {file_path.name}: Added import")
    else:
        print(f"✗ {file_path.name}: No existing utils import found")
        return False

    # Find simple endpoints with try-except blocks and refactor them
    # Pattern 1: Simple try-except with ValueError and Exception
    pattern1 = r'(@api_bp\.(?:route|get|post|put|patch|delete)\([^\)]+\)\s*\ndef\s+(\w+)\([^\)]*\):[^\n]*\n\s+)"""[^"]*"""[^\n]*\n\s+try:\s*\n((?:\s+.+(?:\n|$))+?)except ValueError as e:\s*\n\s+return json_error_response\(str\(e\), status_code=400\)\s*\n\s+except Exception as e:\s*\n\s+logger\.error\(f"Error[^"]*": \{e\}"(?:, exc_info=True)?\)\s*\n\s+return json_error_response\("([^"]+)", status_code=500\)'

    def refactor_simple_endpoint(match):
        decorator = match.group(1)
        func_name = match.group(2)
        func_body = match.group(3)
        error_msg = match.group(4)

        # Remove indentation from body (remove first 4 spaces from each line)
        lines = func_body.split('\n')
        dedented_body = '\n    '.join(line.strip() for line in lines if line.strip())

        return f'{decorator}@handle_api_errors("{error_msg}")\ndef {func_name}():\n    """Refactored with @handle_api_errors"""\n    {dedented_body}'

    new_content = re.sub(pattern1, refactor_simple_endpoint, content)

    if new_content != content:
        file_path.write_text(new_content)
        print(f"✓ {file_path.name}: Refactored simple endpoints")
        return True
    else:
        file_path.write_text(content)  # Save the import at least
        print(f"✓ {file_path.name}: Added import (no simple endpoints to refactor)")
        return True


def main():
    """Main function"""
    backend_root = Path(__file__).parent.parent
    routes_dir = backend_root / "api" / "routes"

    files_to_refactor = [
        "categories.py",
        "parameters.py",
        "flows.py"
    ]

    for filename in files_to_refactor:
        file_path = routes_dir / filename
        if file_path.exists():
            print(f"\n--- Processing {filename} ---")
            add_decorator_to_file(file_path)
        else:
            print(f"✗ {filename}: File not found")


if __name__ == "__main__":
    main()
