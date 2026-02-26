#!/usr/bin/env python3
"""
Verification script for batch operations implementation
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from backend.gql_api.types.batch_operation_type import (
            BatchOperationErrorType,
            BatchOperationResultType
        )
        print("✓ Batch operation types imported successfully")
    except Exception as e:
        print(f"✗ Failed to import batch operation types: {e}")
        return False
    
    try:
        from backend.gql_api.mutations.batch_mutations import (
            BatchDeleteEvents,
            BatchUpdateEvents,
            BatchDeleteFlows,
            BatchUpdateFlows,
            BatchMutations
        )
        print("✓ Batch mutations imported successfully")
    except Exception as e:
        print(f"✗ Failed to import batch mutations: {e}")
        return False
    
    return True


def test_type_functionality():
    """Test batch operation type functionality"""
    print("\nTesting type functionality...")
    
    from backend.gql_api.types.batch_operation_type import (
        BatchOperationErrorType,
        BatchOperationResultType
    )
    
    # Test BatchOperationErrorType
    error = BatchOperationErrorType(id=1, error="Test error")
    assert error.id == 1
    assert error.error == "Test error"
    print("✓ BatchOperationErrorType works correctly")
    
    # Test BatchOperationResultType success
    result = BatchOperationResultType.success_result(affected_count=5)
    assert result.success is True
    assert result.affected_count == 5
    assert result.failed_count == 0
    print("✓ BatchOperationResultType.success_result works correctly")
    
    # Test BatchOperationResultType partial success
    errors = [{'id': 1, 'error': 'Failed'}]
    result = BatchOperationResultType.partial_success_result(
        affected_count=3,
        failed_count=1,
        errors=errors
    )
    assert result.success is False
    assert result.affected_count == 3
    assert result.failed_count == 1
    print("✓ BatchOperationResultType.partial_success_result works correctly")
    
    return True


def test_mutation_structure():
    """Test that mutations have correct structure"""
    print("\nTesting mutation structure...")
    
    from backend.gql_api.mutations.batch_mutations import (
        BatchDeleteEvents,
        BatchUpdateEvents,
        BatchDeleteFlows,
        BatchUpdateFlows
    )
    
    # Check that mutations have required fields
    mutations = [
        ('BatchDeleteEvents', BatchDeleteEvents),
        ('BatchUpdateEvents', BatchUpdateEvents),
        ('BatchDeleteFlows', BatchDeleteFlows),
        ('BatchUpdateFlows', BatchUpdateFlows)
    ]
    
    for name, mutation_class in mutations:
        # Check that mutation has Arguments
        assert hasattr(mutation_class, 'Arguments'), f"{name} missing Arguments"
        print(f"✓ {name} has Arguments")
        
        # Check that mutation has output fields
        assert hasattr(mutation_class, 'ok'), f"{name} missing 'ok' field"
        print(f"✓ {name} has 'ok' field")
    
    return True


def test_schema_integration():
    """Test that mutations are integrated into schema"""
    print("\nTesting schema integration...")
    
    try:
        from backend.gql_api.schema import schema
        
        # Check that batch mutations are available
        mutation_type = schema.mutation_type
        assert mutation_type is not None
        print("✓ Schema has mutation type")
        
        # Try to get batch mutation fields
        fields = mutation_type.fields
        assert 'batchDeleteGames' in fields
        print("✓ batchDeleteGames mutation available in schema")
        
        assert 'batchUpdateGames' in fields
        print("✓ batchUpdateGames mutation available in schema")
        
        assert 'batchDeleteEvents' in fields
        print("✓ batchDeleteEvents mutation available in schema")
        
        assert 'batchUpdateEvents' in fields
        print("✓ batchUpdateEvents mutation available in schema")
        
        assert 'batchDeleteFlows' in fields
        print("✓ batchDeleteFlows mutation available in schema")
        
        assert 'batchUpdateFlows' in fields
        print("✓ batchUpdateFlows mutation available in schema")
        
        return True
    except Exception as e:
        print(f"✗ Schema integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Batch Operations Implementation Verification")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Type Functionality", test_type_functionality),
        ("Mutation Structure", test_mutation_structure),
        ("Schema Integration", test_schema_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
