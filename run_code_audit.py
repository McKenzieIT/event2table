#!/usr/bin/env python3
"""
Code Audit Runner
Runs the comprehensive code audit for Event2Table project
"""
import sys
import os

# Add the skill directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.claude', 'skills', 'code-audit'))

from core.runner import main

if __name__ == "__main__":
    sys.argv[0] = "code-audit"
    main()
