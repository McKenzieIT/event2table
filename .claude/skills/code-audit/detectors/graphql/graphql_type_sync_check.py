"""
GraphQL Type Synchronization Detector

Checks for type synchronization between frontend TypeScript and backend GraphQL schema.

Based on Event2Table GraphQL development standards:
- Frontend enum values must match backend GraphQL schema (case-sensitive)
- Frontend should use generated enum types, not hardcoded strings
- Pydantic models must include all fields accessed by Service layer
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple

from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class GraphQLTypeSyncDetector(BaseDetector):
    """
    Detects GraphQL type synchronization issues

    Rules:
    1. Frontend enum values must match backend GraphQL schema (UPPER_SNAKE_CASE)
    2. Frontend should use generated enum types, not hardcoded strings
    3. Backend GraphQL enums must use UPPER_SNAKE_CASE (GraphQL standard)
    """

    # GraphQL enum patterns
    GRAPHQL_ENUM_PATTERN = r'enum\s+(\w+)\s*\{([^}]+)\}'

    # Common GraphQL enum types in Event2Table
    KNOWN_ENUMS = {
        'HqlJoinType': {'LEFT_JOIN', 'RIGHT_JOIN', 'INNER_JOIN', 'FULL_JOIN', 'LEFT_SEMI_JOIN', 'LEFT_ANTI_JOIN'},
        'NodeType': {'EVENT', 'JOIN', 'UNION', 'FILTER', 'SORT', 'AGGREGATE'},
        'JoinType': {'LEFT', 'RIGHT', 'INNER', 'FULL', 'LEFT_SEMI', 'LEFT_ANTI'},
        'OperatorType': {'EQ', 'NE', 'GT', 'LT', 'GE', 'LE', 'LIKE', 'IN', 'NOT_IN', 'IS_NULL', 'IS_NOT_NULL'},
    }

    def __init__(self):
        super().__init__()
        self.rule_id = "GRAPHQL_SYNC_001"

    def is_applicable(self, file_path: str) -> bool:
        """
        Check if detector applies to this file

        Analyze both backend GraphQL schema files and frontend TypeScript files
        """
        path = Path(file_path)
        return (
            # Backend GraphQL files
            (path.suffix in {'.graphql', '.gql'} and 'backend' in str(path)) or
            # Frontend TypeScript files
            (path.suffix in {'.ts', '.tsx'} and 'frontend' in str(path) and
             'node_modules' not in str(path) and
             'generated' not in str(path).lower())
        )

    def detect(self, file_path: str) -> List[Issue]:
        """Detect GraphQL type synchronization issues"""
        issues = []

        try:
            path = Path(file_path)

            if path.suffix in {'.graphql', '.gql'}:
                # Analyze backend GraphQL schema
                issues.extend(self._check_graphql_schema(file_path))

            elif path.suffix in {'.ts', '.tsx'}:
                # Analyze frontend TypeScript code
                issues.extend(self._check_typescript_enums(file_path))

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _check_graphql_schema(self, file_path: str) -> List[Issue]:
        """Check GraphQL schema enum definitions"""
        issues = []

        try:
            content = Path(file_path).read_text()
            lines = content.split('\n')

            # Find enum definitions
            for line_num, line in enumerate(lines, 1):
                # Check enum definition
                match = re.search(self.GRAPHQL_ENUM_PATTERN, line)
                if match:
                    enum_name = match.group(1)
                    enum_values_block = match.group(2)

                    # Check if enum name follows UPPER_SNAKE_CASE
                    if not self._is_upper_snake_case(enum_name):
                        issues.append(Issue(
                            file_path=file_path,
                            line_number=line_num,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.ARCHITECTURE,
                            message=f"GraphQL enum name should use UPPER_SNAKE_CASE: {enum_name}",
                            suggestion="Rename enum to use UPPER_SNAKE_CASE (e.g., HqlJoinType instead of hqlJoinType)",
                            code_snippet=line.strip(),
                            rule_id=self.rule_id
                        ))

                    # Extract enum values
                    enum_values = self._extract_enum_values(enum_values_block)

                    # Check if enum values follow UPPER_SNAKE_CASE
                    for value in enum_values:
                        if not self._is_upper_snake_case(value):
                            issues.append(Issue(
                                file_path=file_path,
                                line_number=line_num,
                                severity=Severity.HIGH,
                                category=IssueCategory.ARCHITECTURE,
                                message=f"GraphQL enum value should use UPPER_SNAKE_CASE: {enum_name}.{value}",
                                suggestion="Change enum value to UPPER_SNAKE_CASE (e.g., LEFT_JOIN instead of LEFT-JOIN or leftJoin)",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id,
                                metadata={'enum_name': enum_name, 'value': value}
                            ))

        except Exception as e:
            print(f"Error parsing GraphQL schema {file_path}: {e}")

        return issues

    def _check_typescript_enums(self, file_path: str) -> List[Issue]:
        """Check TypeScript enum definitions and usage"""
        issues = []

        try:
            content = Path(file_path).read_text()
            lines = content.split('\n')

            # Find enum definitions
            for line_num, line in enumerate(lines, 1):
                # Check TypeScript enum definition
                match = re.match(r'enum\s+(\w+)\s*\{', line)
                if match:
                    enum_name = match.group(1)

                    # Check if this is a GraphQL-related enum
                    if 'GraphQL' in enum_name or 'Graphql' in enum_name or any(kw in enum_name for kw in ['Join', 'Node', 'Operator', 'Type']):
                        # Extract enum values from following lines
                        enum_values = self._extract_ts_enum_values(lines, line_num)

                        # Check if enum values match GraphQL UPPER_SNAKE_CASE standard
                        for value_line, value in enum_values:
                            if not self._is_upper_snake_case(value):
                                issues.append(Issue(
                                    file_path=file_path,
                                    line_number=value_line,
                                    severity=Severity.HIGH,
                                    category=IssueCategory.ARCHITECTURE,
                                    message=f"TypeScript enum value should match GraphQL UPPER_SNAKE_CASE: {enum_name}.{value}",
                                    suggestion="Change enum value to UPPER_SNAKE_CASE to match backend GraphQL schema",
                                    code_snippet=value,
                                    rule_id=self.rule_id,
                                    metadata={'enum_name': enum_name, 'value': value}
                                ))

                # Check for hardcoded GraphQL enum strings in mutations/queries
                # Pattern: joinType: "LEFT-JOIN" or joinType: 'LEFT-JOIN'
                hardcoded_enum_pattern = r'["\']([A-Z]+(?:_[A-Z]+)*["\']["\']'
                for match in re.finditer(hardcoded_enum_pattern, line):
                    enum_value = match.group(1)
                    # Check if this looks like a GraphQL enum value
                    if '_' in enum_value and enum_value.isupper():
                        issues.append(Issue(
                            file_path=file_path,
                            line_number=line_num,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.QUALITY,
                            message=f"Hardcoded GraphQL enum value detected: {enum_value}",
                            suggestion="Use generated TypeScript enum types instead of hardcoded strings for type safety",
                            code_snippet=line.strip(),
                            rule_id=self.rule_id,
                            metadata={'enum_value': enum_value}
                        ))

        except Exception as e:
            print(f"Error parsing TypeScript file {file_path}: {e}")

        return issues

    def _extract_enum_values(self, values_block: str) -> Set[str]:
        """Extract enum values from GraphQL enum definition block"""
        values = set()
        # Split by comma and extract value names
        for part in values_block.split(','):
            # Remove comments and whitespace
            part = re.sub(r'#.*$', '', part).strip()
            if part:
                # Extract the value name (before any = or ( character)
                value_match = re.match(r'(\w+)', part)
                if value_match:
                    values.add(value_match.group(1))
        return values

    def _extract_ts_enum_values(self, lines: List[str], start_line: int) -> List[Tuple[int, str]]:
        """Extract enum values from TypeScript enum definition"""
        values = []
        indent_level = len(lines[start_line - 1]) - len(lines[start_line - 1].lstrip())

        # Parse enum values until closing brace
        for i in range(start_line, min(start_line + 50, len(lines))):
            line = lines[i].strip()
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue

            if line.startswith('}'):
                break

            # Extract enum value
            match = re.match(r'(\w+)\s*(?:=|$)', line)
            if match:
                value_name = match.group(1)
                if value_name not in {'true', 'false', 'null'}:  # Skip special values
                    values.append((i + 1, value_name))

        return values

    def _is_upper_snake_case(self, name: str) -> bool:
        """Check if name follows UPPER_SNAKE_CASE convention"""
        return bool(re.match(r'^[A-Z]+(_[A-Z]+)*$', name))
