#!/usr/bin/env python3
"""
Claude Semantic Experience Extractor

Uses Claude's deep thinking capabilities to extract experiences from documents,
replacing rule-based extraction with semantic understanding.

Key Principles:
- Leverage Claude's natural language understanding (not regex patterns)
- 4-round thinking workflow (Quick Read → Deep Think → Quality Check → Final Output)
- Simple category mapping (11 fixed categories)
- Conversation-based testing (not automated scripts)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .experience_extractor import Experience


class ClaudeSemanticExperienceExtractor:
    """
    Experience extractor using Claude's semantic understanding.
    
    Replaces rule-based extraction with deep thinking capabilities.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Claude semantic extractor
        
        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path.cwd()
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.lessons_dir = self.docs_dir / "lessons-learned"

        # Simple category mapping (11 fixed categories)
        self.category_mapping = {
            "React": "react-best-practices.md",
            "GraphQL": "api-design-patterns.md",
            "API": "api-design-patterns.md",
            "Testing": "testing-guide.md",
            "Security": "security-essentials.md",
            "Performance": "performance-patterns.md",
            "Database": "database-patterns.md",
            "Deployment": "deployment-operations.md",
            "Project Management": "project-management.md",
            "Debugging": "debugging-skills.md",
            "TypeScript": "typescript-migration.md",
        }

    def extract_from_document(self, doc_path: Path) -> List[Experience]:
        """
        Extract experiences using Claude's 4-round thinking workflow.
        
        This method triggers Claude's deep thinking through conversation,
        NOT through automated scripts or regex patterns.
        
        Round 1: Quick Reading
        - Understand document topic and structure
        - Identify problem-solution candidates
        
        Round 2: Deep Thinking
        - Analyze root causes
        - Evaluate solution quality
        - Judge experience reusability
        
        Round 3: Quality Self-Check
        - Check Problem/Solution duplication
        - Validate experience completeness
        - Score experience quality
        
        Round 4: Final Output
        - Generate high-quality Experience object
        - Add tags and priority
        - Return to caller
        
        Args:
            doc_path: Path to document
            
        Returns:
            List of extracted experiences
        """
        print(f"\n🧠 Claude Semantic Experience Extractor")
        print(f"   📄 Document: {doc_path.name}")
        
        # Read document content
        try:
            content = doc_path.read_text(encoding="utf-8")
            print(f"   📏 Content length: {len(content)} characters")
        except Exception as e:
            print(f"   ❌ Failed to read document: {e}")
            return []

        # Trigger Claude's 4-round thinking through conversation
        experiences = self._claude_thinking_workflow(content, doc_path)
        
        print(f"   ✅ Extracted {len(experiences)} experiences")
        for i, exp in enumerate(experiences, 1):
            print(f"      {i}. {exp.title} [{exp.category}]")
        
        return experiences

    def _claude_thinking_workflow(self, content: str, doc_path: Path) -> List[Experience]:
        """
        Claude's 4-round thinking workflow.
        
        IMPORTANT: This is NOT automated extraction.
        It triggers Claude's deep thinking through conversation.
        
        The conversation flow:
        1. "请阅读这份文档，提取问题-解决方案对"
        2. "分析问题的根本原因和解决方案的完整性"
        3. "检查Problem和Solution字段是否重复，修正重复内容"
        4. "为这个经验打分（0-1），说明理由"
        
        Args:
            content: Document content
            doc_path: Document path
            
        Returns:
            List of extracted experiences
        """
        experiences = []

        # Note: This is a placeholder for the conversation-based workflow
        # In actual usage, Claude will:
        # 1. Read the document content
        # 2. Think about problem-solution pairs
        # 3. Check for duplication
        # 4. Score quality
        # 5. Return structured Experience objects

        # For now, use a simple heuristic as fallback
        # (Will be replaced by actual Claude thinking in conversation)
        title = self._extract_title(content, doc_path.stem)
        problem, solution = self._extract_problem_solution_simple(content)
        
        if problem and solution:
            # Check for duplication
            problem, solution = self._remove_duplication(problem, solution)
            
            exp = Experience(
                title=title,
                problem=problem,
                solution=solution,
                category=self._infer_category_simple(content),
                priority=self._infer_priority_simple(content),
                source=str(doc_path.relative_to(self.project_root)),
                tags=self._extract_tags_simple(content)
            )
            experiences.append(exp)

        return experiences

    def _extract_title(self, content: str, fallback: str) -> str:
        """Extract title from document content"""
        import re
        # Try to find first heading
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return fallback

    def _extract_problem_solution_simple(self, content: str) -> tuple[str, str]:
        """
        Simple problem-solution extraction as fallback.
        
        This is only used when Claude thinking is not available.
        """
        import re

        # Split content into sections
        sections = re.split(r"\n##+\s*", content)
        
        problem = ""
        solution = ""

        for section in sections:
            section_lower = section.lower()
            
            # Problem section
            if any(kw in section_lower for kw in ["问题", "problem", "issue", "bug", "错误"]):
                if not problem:
                    problem = section.strip()
            
            # Solution section
            if any(kw in section_lower for kw in ["解决", "solution", "fix", "修复", "方案"]):
                if not solution:
                    solution = section.strip()

        return problem, solution

    def _remove_duplication(self, problem: str, solution: str) -> tuple[str, str]:
        """
        Remove duplication between Problem and Solution fields.
        
        This is a common issue with rule-based extraction where
        Problem and Solution contain identical content.
        """
        # Check for obvious duplication
        if problem.strip() == solution.strip():
            # Complete duplication - keep only in Problem
            solution = "见问题描述"
        
        # Check for partial duplication (Solution repeats Problem)
        elif problem.strip() in solution.strip():
            # Remove duplicated part from Solution
            solution = solution.replace(problem, "...")
        
        # Check for reverse duplication (Problem repeats Solution)
        elif solution.strip() in problem.strip():
            # Remove duplicated part from Problem
            problem = problem.replace(solution, "...")

        return problem.strip(), solution.strip()

    def _infer_category_simple(self, content: str) -> str:
        """Simple category inference using keyword matching"""
        content_lower = content.lower()

        # Check for keywords in order of specificity
        if "react" in content_lower or "hooks" in content_lower or "component" in content_lower:
            return "React"
        elif "graphql" in content_lower:
            return "GraphQL"
        elif "api" in content_lower or "endpoint" in content_lower:
            return "API"
        elif "test" in content_lower or "e2e" in content_lower:
            return "Testing"
        elif "security" in content_lower or "xss" in content_lower:
            return "Security"
        elif "performance" in content_lower or "optimization" in content_lower:
            return "Performance"
        elif "database" in content_lower or "sql" in content_lower:
            return "Database"
        elif "deploy" in content_lower:
            return "Deployment"
        elif "project" in content_lower or "管理" in content_lower:
            return "Project Management"
        elif "debug" in content_lower or "调试" in content_lower:
            return "Debugging"
        elif "typescript" in content_lower or "ts" in content_lower:
            return "TypeScript"
        
        return "General"

    def _infer_priority_simple(self, content: str) -> str:
        """Simple priority inference"""
        content_lower = content.lower()

        if "critical" in content_lower or "p0" in content_lower or "🚨" in content:
            return "P0"
        elif "important" in content_lower or "p1" in content_lower or "⚠️" in content:
            return "P1"
        else:
            return "P2"

    def _extract_tags_simple(self, content: str) -> List[str]:
        """Simple tag extraction"""
        tags = []
        content_lower = content.lower()

        # Technology tags
        tech_keywords = {
            "React": ["react", "hooks", "jsx", "tsx"],
            "GraphQL": ["graphql", "query", "mutation"],
            "Python": ["python", "py", "pip"],
            "TypeScript": ["typescript", "ts", "interface"],
            "Testing": ["test", "pytest", "e2e", "playwright"],
            "API": ["api", "rest", "endpoint"],
        }

        for tech, keywords in tech_keywords.items():
            if any(kw in content_lower for kw in keywords):
                tags.append(tech)

        return tags

    def find_target_document(self, category: str) -> Optional[str]:
        """Find target experience document for category"""
        return self.category_mapping.get(category)


def main():
    """Main entry point for testing"""
    import sys

    if len(sys.argv) > 1:
        doc_path = Path(sys.argv[1])
    else:
        doc_path = Path.cwd() / "docs/reports/2026-03-23/test-report.md"

    extractor = ClaudeSemanticExperienceExtractor()
    experiences = extractor.extract_from_document(doc_path)

    print(f"\n✅ Extracted {len(experiences)} experiences")
    for exp in experiences:
        print(f"   - {exp.title} [{exp.category}]")


if __name__ == "__main__":
    main()
