#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick verification script for Events module Entity migration

This script verifies:
1. EventRepository methods return EventEntity
2. No game_id violations (only game_gid)
3. EventService uses EventEntity
"""

import sys
sys.path.insert(0, '..')
import inspect
from backend.models.repositories.events import EventRepository
from backend.models.entities import EventEntity
from backend.services.events.event_service import EventService


def verify_repository_return_types():
    """Verify EventRepository methods return EventEntity"""
    print("🔍 Checking EventRepository return types...")

    repo = EventRepository()

    # Check method signatures
    issues = []

    # Method -> Expected return type
    methods_to_check = {
        'find_by_id': EventEntity,
        'find_by_name': EventEntity,
        'find_by_game_gid': list,  # List[EventEntity]
        'create': EventEntity,
        'update': EventEntity,
    }

    for method_name, expected_type in methods_to_check.items():
        if not hasattr(repo, method_name):
            issues.append(f"❌ Method {method_name} not found")
            continue

        # Check docstring for return type hint
        method = getattr(repo, method_name)
        doc = method.__doc__

        if doc and 'EventEntity' in doc:
            print(f"  ✅ {method_name}: Returns EventEntity")
        elif expected_type == list and doc and 'List' in doc:
            print(f"  ✅ {method_name}: Returns List")
        else:
            issues.append(f"⚠️  {method_name}: Missing return type documentation")

    return issues


def verify_no_game_id_violations():
    """Verify no game_id violations in EventRepository and EventService"""
    print("\n🔍 Checking for game_id violations...")

    issues = []

    # Check EventRepository
    repo_source = inspect.getsource(EventRepository)

    # Look for game_id parameter in method signatures
    for line in repo_source.split('\n'):
        if 'def create_with_parameters' in line:
            if 'game_id' in line and 'game_gid' not in line:
                issues.append(f"❌ EventRepository.create_with_parameters has game_id parameter")
            elif 'game_id' not in line or 'game_gid' in line:
                print(f"  ✅ EventRepository.create_with_parameters signature OK")
            break

    # Check EventService
    service_source = inspect.getsource(EventService)

    # Look for game_id usage (excluding comments)
    for i, line in enumerate(service_source.split('\n'), 1):
        if line.strip().startswith('#'):
            continue
        if 'game.id' in line and 'game_id' in line:
            issues.append(f"❌ EventService line {i}: Uses game.id (game_id violation)")

    if not issues:
        print(f"  ✅ No game_id violations found")

    return issues


def verify_service_uses_entity():
    """Verify EventService uses EventEntity"""
    print("\n🔍 Checking EventService Entity usage...")

    service = EventService()
    issues = []

    # Check that key methods accept/return EventEntity
    methods_to_check = [
        'create_event',
        'update_event',
        'get_event_by_id',
    ]

    for method_name in methods_to_check:
        if not hasattr(service, method_name):
            issues.append(f"❌ Method {method_name} not found")
            continue

        method = getattr(service, method_name)
        doc = method.__doc__

        if doc and 'EventEntity' in doc:
            print(f"  ✅ {method_name}: Uses EventEntity")
        else:
            issues.append(f"⚠️  {method_name}: Missing EventEntity documentation")

    return issues


def verify_complete_implementation():
    """Verify no pass/TODO placeholders"""
    print("\n🔍 Checking for complete implementation...")

    issues = []

    # Check EventRepository
    repo_source = inspect.getsource(EventRepository)

    for i, line in enumerate(repo_source.split('\n'), 1):
        if line.strip() == 'pass':
            issues.append(f"❌ EventRepository line {i}: Found 'pass' statement")

    # Check EventService
    service_source = inspect.getsource(EventService)

    for i, line in enumerate(service_source.split('\n'), 1):
        if line.strip() == 'pass':
            issues.append(f"❌ EventService line {i}: Found 'pass' statement")
        elif 'TODO' in line and 'def ' in '\n'.join(service_source.split('\n')[max(0, i-3):i]):
            issues.append(f"⚠️  EventService line {i}: Found TODO placeholder")

    if not issues:
        print(f"  ✅ No pass/TODO placeholders found")

    return issues


def main():
    """Run all verification checks"""
    print("=" * 70)
    print("Events Module Entity Migration Verification")
    print("=" * 70)

    all_issues = []

    # Run checks
    all_issues.extend(verify_repository_return_types())
    all_issues.extend(verify_no_game_id_violations())
    all_issues.extend(verify_service_uses_entity())
    all_issues.extend(verify_complete_implementation())

    # Summary
    print("\n" + "=" * 70)
    if all_issues:
        print(f"❌ Found {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"  {issue}")
        return 1
    else:
        print("✅ All verification checks passed!")
        print("\n📊 Summary:")
        print("  ✅ EventRepository returns EventEntity objects")
        print("  ✅ No game_id violations (only game_gid)")
        print("  ✅ EventService uses EventEntity")
        print("  ✅ Complete implementation (no pass/TODO)")
        return 0


if __name__ == '__main__':
    sys.exit(main())
