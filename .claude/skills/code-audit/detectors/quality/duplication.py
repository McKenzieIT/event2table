"""
Code Duplication Detector

Detects duplicate code blocks.
"""

from pathlib import Path
from typing import List, Dict
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class DuplicationDetector(BaseDetector):
    """
    Detects code duplication

    Strategy:
    - Hash-based line sequence matching
    - Detects copy-pasted code blocks
    """

    def __init__(self, min_lines: int = 5):
        super().__init__()
        self.rule_id = "QUAL_DUP_001"
        self.min_lines = min_lines
        self.code_blocks: Dict[str, List[tuple]] = {}

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect code duplication"""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\n')

            # Extract code blocks
            blocks = self._extract_blocks(lines)

            # Check for duplicates
            for block_hash, locations in blocks.items():
                if len(locations) > 1:
                    for line_num in locations[1:]:  # Skip first occurrence
                        issues.append(Issue(
                            file_path=str(file_path),
                            line_number=line_num,
                            severity=Severity.LOW,
                            category=IssueCategory.QUALITY,
                            message=f"Duplicated code block ({len(locations)} occurrences)",
                            suggestion="Extract duplicated code into a function",
                            rule_id=self.rule_id
                        ))

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _extract_blocks(self, lines: List[str]) -> Dict[str, List[int]]:
        """Extract code blocks and return hash map"""
        blocks = {}

        for i in range(len(lines) - self.min_lines + 1):
            block = '\n'.join(lines[i:i + self.min_lines])
            block_hash = hash(block.strip())

            if block_hash not in blocks:
                blocks[block_hash] = []
            blocks[block_hash].append(i + 1)

        return blocks
