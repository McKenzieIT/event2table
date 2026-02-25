#!/usr/bin/env python3
"""Test GraphQL endpoint configuration"""

import sys
sys.path.insert(0, '/Users/mckenzie/Documents/event2table')

try:
    from backend.gql_api.schema import schema
    print("✅ Schema imported successfully")
    print(f"Schema query type: {schema.query}")
    print(f"Schema mutation type: {schema.mutation}")
except Exception as e:
    print(f"❌ Schema import failed: {e}")
    sys.exit(1)

try:
    from flask_graphql import GraphQLView
    print("✅ Flask-GraphQL imported successfully")
except Exception as e:
    print(f"❌ Flask-GraphQL import failed: {e}")
    sys.exit(1)

print("\n✅ All GraphQL dependencies are installed correctly")
print("\nPlease restart the Flask server:")
print("  1. Kill existing process: kill $(ps aux | grep 'python.*web_app' | grep -v grep | awk '{print $2}')")
print("  2. Start server: python3 web_app.py")
