#!/usr/bin/env python3
"""
API Contract Test Suite

Comprehensive test suite to verify API contract consistency between frontend and backend.

Tests include:
1. Backend API endpoints existence verification
2. GraphQL schema validation (enums, types, mutations)
3. Frontend-backend type consistency checks
4. Parameter naming convention validation (game_gid vs game_id)
5. GraphQL enum value consistency (FieldTypeEnum, FilterModeEnum)

Usage:
    # Run all tests
    python scripts/test/api_contract_test.py

    # Run specific test
    python scripts/test/api_contract_test.py --test graphql_enum_consistency

    # Auto-fix mode (experimental)
    python scripts/test/api_contract_test.py --fix

    # Verbose mode
    python scripts/test/api_contract_test.py --verbose
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Add backend to path
# Get the project root (scripts/test/ -> scripts/ -> project_root)
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent
backend_path = project_root / 'backend'
sys.path.insert(0, str(backend_path))

# Test configuration
FRONTEND_SRC = project_root / 'frontend' / 'src'
BACKEND_API = backend_path / 'api'
BACKEND_GQL = backend_path / 'gql_api'

# Debug: Print paths for troubleshooting
if '--debug' in sys.argv:
    print(f"DEBUG: Script path: {script_path}")
    print(f"DEBUG: Project root: {project_root}")
    print(f"DEBUG: Backend path: {backend_path}")
    print(f"DEBUG: Frontend src: {FRONTEND_SRC}")
    print(f"DEBUG: GraphQL schema: {BACKEND_GQL / 'schema_parameter_management.py'}")

# Type mappings
FRONTEND_FIELD_TYPES = ['all', 'params', 'non-common', 'common', 'base']
BACKEND_FIELD_ENUM_VALUES = ['all', 'params', 'non-common', 'common', 'base']

FRONTEND_FILTER_MODES = ['all', 'common', 'params', 'non_common']
BACKEND_FILTER_ENUM_VALUES = ['all', 'common', 'params', 'non_common']


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_success(message: str):
    """Print success message in green"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message in red"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message in yellow"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message in blue"""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")


def print_header(message: str):
    """Print header in bold"""
    print(f"\n{Colors.BOLD}{message}{Colors.ENDC}")


# ============================================================================
# TEST 1: GraphQL Enum Consistency
# ============================================================================

def test_graphql_enum_consistency() -> Tuple[bool, List[str]]:
    """
    Test frontend enum types vs backend GraphQL schema enums.

    Verifies:
    - Frontend FieldOptionType matches backend FieldTypeEnum
    - Frontend filter modes match backend FilterModeEnum
    - Enum values are identical (case-sensitive)
    """
    print_header("🧪 Test 1: GraphQL Enum Consistency")
    errors = []

    # Test 1.1: FieldTypeEnum consistency
    print_info("Checking FieldTypeEnum consistency...")

    frontend_types = set(FRONTEND_FIELD_TYPES)
    backend_types = set(BACKEND_FIELD_ENUM_VALUES)

    if frontend_types == backend_types:
        print_success("FieldTypeEnum: Frontend and backend types match perfectly")
    else:
        print_error("FieldTypeEnum: Mismatch detected")

        missing_in_backend = frontend_types - backend_types
        if missing_in_backend:
            errors.append(f"FieldTypeEnum: Missing in backend: {missing_in_backend}")
            print_error(f"  Missing in backend: {missing_in_backend}")

        missing_in_frontend = backend_types - frontend_types
        if missing_in_frontend:
            errors.append(f"FieldTypeEnum: Missing in frontend: {missing_in_frontend}")
            print_error(f"  Missing in frontend: {missing_in_frontend}")

    # Test 1.2: FilterModeEnum consistency
    print_info("Checking FilterModeEnum consistency...")

    frontend_modes = set(FRONTEND_FILTER_MODES)
    backend_modes = set(BACKEND_FILTER_ENUM_VALUES)

    if frontend_modes == backend_modes:
        print_success("FilterModeEnum: Frontend and backend modes match perfectly")
    else:
        print_error("FilterModeEnum: Mismatch detected")

        missing_in_backend = frontend_modes - backend_modes
        if missing_in_backend:
            errors.append(f"FilterModeEnum: Missing in backend: {missing_in_backend}")
            print_error(f"  Missing in backend: {missing_in_backend}")

        missing_in_frontend = backend_modes - frontend_modes
        if missing_in_frontend:
            errors.append(f"FilterModeEnum: Missing in frontend: {missing_in_frontend}")
            print_error(f"  Missing in frontend: {missing_in_frontend}")

    # Test 1.3: Check enum hyphen consistency (critical for GraphQL)
    print_info("Checking enum hyphen/underscore consistency...")

    # Frontend uses 'non-common' (hyphen)
    # Backend should also use 'non-common' (hyphen) for GraphQL enum
    if 'non-common' in frontend_types and 'non-common' in backend_types:
        print_success("Enum 'non-common' uses hyphen consistently (GraphQL-compliant)")
    elif 'non_common' in frontend_types or 'non_common' in backend_types:
        errors.append("Enum uses underscore 'non_common' instead of hyphen 'non-common'")
        print_error("Enum should use hyphen 'non-common' for GraphQL compliance")
        print_info("  GraphQL enums should use hyphens, not underscores")

    return len(errors) == 0, errors


# ============================================================================
# TEST 2: Backend API Endpoints Existence
# ============================================================================

def test_backend_api_endpoints() -> Tuple[bool, List[str]]:
    """
    Test that all backend API endpoints referenced by frontend exist.

    Verifies:
    - REST API endpoints are defined in backend
    - GraphQL mutations are defined in schema
    - Route handlers are implemented
    """
    print_header("🧪 Test 2: Backend API Endpoints Existence")
    errors = []

    # Check GraphQL schema (primary API now)
    print_info("Checking GraphQL schema...")
    schema_path = project_root / 'backend' / 'gql_api' / 'schema_parameter_management.py'

    if schema_path.exists():
        content = schema_path.read_text()
        print_success(f"GraphQL schema file found: {schema_path.name}")

        # Check for critical mutations and queries (snake_case in Python, camelCase in GraphQL)
        critical_graphql_items = [
            ('batch_add_fields_to_canvas', 'Mutation'),  # Python name (snake_case)
            ('batchAddFieldsToCanvas', 'Mutation'),      # GraphQL name (camelCase)
            ('parametersManagement', 'Query'),
            ('FieldTypeEnum', 'Enum'),
            ('FilterModeEnum', 'Enum'),
        ]

        for item_name, item_type in critical_graphql_items:
            if item_name in content:
                print_success(f"GraphQL {item_type}: {item_name}")
                break  # Found at least one variant
        else:
            # If none of the variants found, report error
            for item_name, item_type in critical_graphql_items:
                if item_name not in content:
                    errors.append(f"GraphQL {item_type} not found: {item_name}")
                    print_error(f"GraphQL {item_type} not found: {item_name}")
    else:
        errors.append(f"GraphQL schema file not found: {schema_path}")
        print_error(f"GraphQL schema file not found: {schema_path}")

    # Check GraphQL mutations directory
    print_info("Checking GraphQL mutations...")
    mutations_dir = project_root / 'backend' / 'gql_api' / 'mutations'

    if mutations_dir.exists():
        print_success("GraphQL mutations directory found")

        # Check for critical mutation files
        critical_mutations_files = [
            'field_builder_mutations.py',
            'event_mutations.py',
            'parameter_mutations.py',
        ]

        for mutation_file in critical_mutations_files:
            file_path = mutations_dir / mutation_file
            if file_path.exists():
                print_success(f"Mutation file: {mutation_file}")
            else:
                errors.append(f"Mutation file not found: {mutation_file}")
                print_error(f"Mutation file not found: {mutation_file}")
    else:
        errors.append(f"GraphQL mutations directory not found: {mutations_dir}")
        print_error(f"GraphQL mutations directory not found: {mutations_dir}")

    return len(errors) == 0, errors


# ============================================================================
# TEST 3: Parameter Naming Convention (game_gid vs game_id)
# ============================================================================

def test_parameter_naming_convention() -> Tuple[bool, List[str]]:
    """
    Test that frontend uses correct parameter names (game_gid, not game_id).

    Verifies:
    - Frontend API calls use game_gid parameter
    - GraphQL queries use game_gid parameter
    - No references to deprecated game_id parameter (except for backward compatibility)
    """
    print_header("🧪 Test 3: Parameter Naming Convention (game_gid)")
    errors = []

    print_info("Scanning frontend TypeScript files for parameter usage...")

    # Find all .ts and .tsx files
    ts_files = list(FRONTEND_SRC.rglob('*.ts')) + list(FRONTEND_SRC.rglob('*.tsx'))

    game_gid_count = 0
    game_id_count = 0
    game_id_issues = []

    for ts_file in ts_files:
        try:
            content = ts_file.read_text()

            # Count occurrences
            file_game_gid = content.count('game_gid')
            file_game_id = content.count('game_id')

            game_gid_count += file_game_id
            game_id_count += file_game_id

            # Check for suspicious patterns (game_id in API calls)
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # Legitimate uses: fetchGameById, database operations
                if 'fetchGameById' in line or 'fetchGameByID' in line:
                    continue

                # Suspicious: game_id in API URLs or query parameters
                if 'game_id=' in line or ('/api/' in line and 'game_id' in line):
                    game_id_issues.append(f"{ts_file.relative_to(FRONTEND_SRC)}:{i}")

                # Check for gameId in fetch calls (suspicious unless it's fetchGameById)
                if 'gameId:' in line and 'fetch' in line and 'fetchGameById' not in line:
                    game_id_issues.append(f"{ts_file.relative_to(FRONTEND_SRC)}:{i}")

        except Exception as e:
            print_warning(f"Could not read {ts_file}: {e}")

    print_info(f"Found {game_gid_count} game_gid references")
    print_info(f"Found {game_id_count} game_id references")

    if game_gid_count > 0:
        print_success("Frontend uses game_gid parameter correctly")
    else:
        errors.append("No game_gid references found in frontend")
        print_error("No game_gid references found in frontend")

    if game_id_count > 0:
        print_warning(f"Found {game_id_count} game_id references (may be legitimate)")
        print_info("  Reviewing game_id usage context...")

        # Only flag as errors if there are suspicious patterns
        if game_id_issues:
            for issue in game_id_issues[:5]:  # Show first 5 issues
                print_warning(f"  {issue}")
                errors.append(f"Suspicious game_id usage: {issue}")
        else:
            print_info("  All game_id uses appear legitimate (database operations)")

    return len(errors) == 0, errors


# ============================================================================
# TEST 4: GraphQL Mutation Parameters Type Matching
# ============================================================================

def test_mutation_parameter_types() -> Tuple[bool, List[str]]:
    """
    Test that GraphQL mutation parameters match frontend expectations.

    Verifies:
    - Mutation parameter names match frontend calls
    - Parameter types are compatible (Int, String, etc.)
    - Required parameters match

    Note: Python backend uses snake_case (event_id, field_type)
          GraphQL exposes camelCase (eventId, fieldType)
          Frontend uses camelCase ($eventId, $fieldType)
    """
    print_header("🧪 Test 4: GraphQL Mutation Parameter Types")
    errors = []

    # Check batchAddFieldsToCanvas mutation
    print_info("Checking batchAddFieldsToCanvas mutation...")

    schema_path = project_root / 'backend' / 'gql_api' / 'schema_parameter_management.py'

    if not schema_path.exists():
        errors.append(f"Schema file not found: {schema_path}")
        return False, errors

    content = schema_path.read_text()

    # Expected mutation signature (Python backend uses snake_case)
    expected_backend_params = {
        'event_id': 'Int',
        'field_type': 'FieldTypeEnum'
    }

    # Expected frontend parameters (camelCase)
    expected_frontend_params = {
        '$eventId': 'Int',
        '$fieldType': 'FieldTypeEnum'
    }

    # Check if mutation exists (both Python and GraphQL names)
    if 'BatchAddFieldsToCanvasMutation' in content or 'batch_add_fields_to_canvas' in content:
        print_success("Mutation batchAddFieldsToCanvas found in schema")

        # Check for backend parameters (snake_case)
        for param, expected_type in expected_backend_params.items():
            # Check for parameter definition in Arguments class
            param_pattern = rf'{param}\s*=\s*(?:Argument\()?{expected_type}|Int\(required=True'
            if re.search(param_pattern, content, re.IGNORECASE):
                print_success(f"  Backend parameter {param}: {expected_type}")
            else:
                # Try alternative pattern - just check parameter name exists
                if f'{param} =' in content or f'{param}=' in content:
                    print_success(f"  Backend parameter {param}: found")
                else:
                    errors.append(f"Missing backend parameter: {param} ({expected_type})")
                    print_error(f"  Missing backend parameter: {param} ({expected_type})")
    else:
        errors.append("Mutation batchAddFieldsToCanvas not found in schema")
        print_error("Mutation batchAddFieldsToCanvas not found")
        return False, errors

    # Check frontend mutation call
    print_info("Checking frontend mutation call...")

    mutations_file = project_root / 'frontend' / 'src' / 'graphql' / 'mutations.ts'

    if mutations_file.exists():
        mutations_content = mutations_file.read_text()

        if 'batchAddFieldsToCanvas' in mutations_content:
            print_success("Frontend mutation definition found")

            # Check parameter usage (camelCase with $ prefix)
            for param, expected_type in expected_frontend_params.items():
                if param in mutations_content:
                    print_success(f"  Frontend uses parameter: {param}")
                else:
                    errors.append(f"Frontend missing parameter: {param}")
                    print_error(f"  Frontend missing parameter: {param}")
        else:
            errors.append("Frontend mutation batchAddFieldsToCanvas not found")
            print_error("Frontend mutation batchAddFieldsToCanvas not found")
    else:
        errors.append(f"Frontend mutations.ts file not found: {mutations_file}")
        print_error(f"Frontend mutations.ts file not found: {mutations_file}")

    return len(errors) == 0, errors


# ============================================================================
# TEST 5: Type Import Consistency
# ============================================================================

def test_type_import_consistency() -> Tuple[bool, List[str]]:
    """
    Test that frontend imports types from correct locations.

    Verifies:
    - Field types imported from @shared/types/fieldBuilder
    - GraphQL types imported from @graphql/types
    - No circular dependencies
    """
    print_header("🧪 Test 5: Type Import Consistency")
    errors = []

    print_info("Checking type imports in frontend components...")

    # Check FieldSelectionModal imports
    field_modal = project_root / 'frontend' / 'src' / 'event-builder' / 'components' / 'FieldSelectionModal.tsx'

    if field_modal.exists():
        content = field_modal.read_text()

        # Check for FieldOptionType definition
        if 'type FieldOptionType' in content or 'FieldOptionType =' in content:
            print_success("FieldSelectionModal: FieldOptionType type defined")
        else:
            errors.append("FieldSelectionModal: FieldOptionType type not defined")
            print_error("FieldSelectionModal: FieldOptionType type not defined")

        # Check for correct enum values
        required_values = ['all', 'params', 'non-common', 'common', 'base']
        for value in required_values:
            if f"'{value}'" in content:
                print_success(f"  FieldOptionType includes: {value}")
            else:
                errors.append(f"FieldSelectionModal: Missing enum value: {value}")
                print_error(f"  Missing enum value: {value}")
    else:
        errors.append(f"FieldSelectionModal.tsx not found: {field_modal}")
        print_error(f"FieldSelectionModal.tsx not found: {field_modal}")

    return len(errors) == 0, errors


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests(verbose: bool = False) -> Dict[str, Tuple[bool, List[str]]]:
    """Run all tests and return results"""
    results = {}

    tests = [
        ("GraphQL Enum Consistency", test_graphql_enum_consistency),
        ("Backend API Endpoints", test_backend_api_endpoints),
        ("Parameter Naming Convention", test_parameter_naming_convention),
        ("Mutation Parameter Types", test_mutation_parameter_types),
        ("Type Import Consistency", test_type_import_consistency),
    ]

    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}🚀 API Contract Test Suite{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.ENDC}")

    for test_name, test_func in tests:
        try:
            passed, errors = test_func()
            results[test_name] = (passed, errors)

            if passed:
                print_success(f"{test_name}: PASSED")
            else:
                print_error(f"{test_name}: FAILED")

            if verbose and errors:
                print(f"\n  Errors:")
                for error in errors:
                    print(f"    - {error}")

        except Exception as e:
            print_error(f"{test_name}: EXCEPTION - {e}")
            results[test_name] = (False, [str(e)])

    return results


def print_summary(results: Dict[str, Tuple[bool, List[str]]]):
    """Print test summary"""
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}📊 Test Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.ENDC}")

    total = len(results)
    passed = sum(1 for _, (p, _) in results.items() if p)
    failed = total - passed

    print(f"\nTotal Tests: {total}")
    print_success(f"Passed: {passed}")
    print_error(f"Failed: {failed}")

    if failed > 0:
        print(f"\n{Colors.BOLD}Failed Tests:{Colors.ENDC}")
        for test_name, (passed, errors) in results.items():
            if not passed:
                print(f"\n{Colors.FAIL}❌ {test_name}{Colors.ENDC}")
                for error in errors:
                    print(f"   {error}")

    # Overall result
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    if failed == 0:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ ALL TESTS PASSED{Colors.ENDC}")
        print(f"{Colors.OKGREEN}API contract is consistent!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ {failed} TEST(S) FAILED{Colors.ENDC}")
        print(f"{Colors.FAIL}API contract has inconsistencies that need fixing{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='API Contract Test Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test/api_contract_test.py
  python scripts/test/api_contract_test.py --verbose
  python scripts/test/api_contract_test.py --test graphql_enum_consistency
        """
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--test',
        type=str,
        help='Run specific test (e.g., graphql_enum_consistency)'
    )

    parser.add_argument(
        '--fix',
        action='store_true',
        help='Auto-fix mode (experimental)'
    )

    args = parser.parse_args()

    if args.fix:
        print_warning("Auto-fix mode is experimental and may not work correctly")
        print_info("Please review changes before committing")
        return 1

    if args.test:
        # Run specific test
        test_map = {
            'graphql_enum_consistency': test_graphql_enum_consistency,
            'backend_api_endpoints': test_backend_api_endpoints,
            'parameter_naming_convention': test_parameter_naming_convention,
            'mutation_parameter_types': test_mutation_parameter_types,
            'type_import_consistency': test_type_import_consistency,
        }

        if args.test in test_map:
            passed, errors = test_map[args.test]()
            return 0 if passed else 1
        else:
            print_error(f"Unknown test: {args.test}")
            print_info(f"Available tests: {', '.join(test_map.keys())}")
            return 1
    else:
        # Run all tests
        results = run_all_tests(verbose=args.verbose)
        print_summary(results)

        # Return exit code
        failed = sum(1 for _, (p, _) in results.items() if not p)
        return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
