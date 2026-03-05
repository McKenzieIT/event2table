#!/usr/bin/env python3
"""
Test Parameters API directly without Flask context
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/Users/mckenzie/Documents/event2table')

# Set environment to avoid GraphQL schema conflicts
os.environ['FLASK_ENV'] = 'testing'

print("=" * 60)
print("Testing Parameters API Components")
print("=" * 60)

# Test 1: Database connection
print("\n1. Testing database connection...")
try:
    import sqlite3
    db_path = '/Users/mckenzie/Documents/event2table/data/dwd_generator.db'
    conn = sqlite3.connect(db_path, timeout=5.0)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM games')
    count = cursor.fetchone()[0]
    print(f"✅ Database connected: {count} games")
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)

# Test 2: Game query
print("\n2. Testing game query...")
try:
    import sqlite3
    conn = sqlite3.connect(db_path, timeout=5.0)
    cursor = conn.cursor()
    cursor.execute('SELECT id, gid, name FROM games WHERE gid = ?', (10000147,))
    row = cursor.fetchone()
    if row:
        print(f"✅ Game found: ID={row[0]}, GID={row[1]}, Name={row[2]}")
    else:
        print("❌ Game not found")
    conn.close()
except Exception as e:
    print(f"❌ Query error: {e}")
    sys.exit(1)

# Test 3: Parameters query
print("\n3. Testing parameters query...")
try:
    conn = sqlite3.connect(db_path, timeout=5.0)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*)
        FROM event_params ep
        INNER JOIN log_events le ON ep.event_id = le.id
        WHERE le.game_gid = ?
    ''', (10000147,))
    count = cursor.fetchone()[0]
    print(f"✅ Parameters count: {count}")
    conn.close()
except Exception as e:
    print(f"❌ Parameters query error: {e}")
    sys.exit(1)

# Test 4: Check if backend process is responsive
print("\n4. Testing backend process...")
try:
    import requests
    response = requests.get('http://127.0.0.1:5001/api/games', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend responsive: {len(data.get('data', []))} games")
    else:
        print(f"❌ Backend error: {response.status_code}")
except Exception as e:
    print(f"❌ Backend connection error: {e}")

# Test 5: Test parameters API
print("\n5. Testing parameters API endpoint...")
try:
    import requests
    response = requests.get(
        'http://127.0.0.1:5001/api/parameters/all',
        params={'game_gid': 10000147, 'page': 1, 'limit': 10},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        params = data.get('data', {}).get('parameters', [])
        total = data.get('data', {}).get('total', 0)
        print(f"✅ Parameters API: {len(params)} params, total={total}")
    else:
        error = data.get('error', 'Unknown error')
        print(f"❌ Parameters API error: {error}")
except Exception as e:
    print(f"❌ Parameters API exception: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
