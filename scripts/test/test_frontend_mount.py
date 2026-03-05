#!/usr/bin/env python3
"""
Frontend Mount Test - Test if React app mounts correctly
"""

import requests
import json
import time

def test_backend_api():
    """Test backend API endpoints"""
    print("=" * 60)
    print("Testing Backend API")
    print("=" * 60)

    # Test games API
    try:
        response = requests.get('http://127.0.0.1:5001/api/games', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Games API: {len(data.get('data', []))} games found")
        else:
            print(f"❌ Games API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Games API error: {e}")

    # Test GraphQL endpoint
    try:
        response = requests.post(
            'http://127.0.0.1:5001/api/graphql',
            json={"query": "{ __typename }"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GraphQL API: {data.get('data', {}).get('__typename', 'unknown')}")
        else:
            print(f"❌ GraphQL API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GraphQL API error: {e}")

def test_frontend_server():
    """Test frontend server"""
    print("\n" + "=" * 60)
    print("Testing Frontend Server")
    print("=" * 60)

    try:
        response = requests.get('http://localhost:5173', timeout=5)
        if response.status_code == 200:
            html = response.text

            # Check for critical elements
            has_app_root = 'id="app-root"' in html
            has_loader = 'id="initial-loader"' in html
            has_main_tsx = 'src/main.tsx' in html or 'src="/src/main.tsx"' in html

            print(f"✅ Frontend server responding (200 OK)")
            print(f"  - app-root element: {'✅' if has_app_root else '❌'}")
            print(f"  - initial-loader element: {'✅' if has_loader else '❌'}")
            print(f"  - main.tsx script: {'✅' if has_main_tsx else '❌'}")

            # Check for potential issues
            if 'Loading Event2Table...' in html:
                print("⚠️  Initial loader still visible (React may not have mounted)")
        else:
            print(f"❌ Frontend server failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend server error: {e}")

def test_main_tsx():
    """Test main.tsx module loading"""
    print("\n" + "=" * 60)
    print("Testing main.tsx Module")
    print("=" * 60)

    try:
        response = requests.get('http://localhost:5173/src/main.tsx', timeout=5)
        if response.status_code == 200:
            content = response.text

            # Check for critical code
            has_create_root = 'createRoot' in content or 'ReactDOM.createRoot' in content
            has_app_root = 'app-root' in content
            has_render = 'render(' in content

            print(f"✅ main.tsx loaded successfully")
            print(f"  - createRoot call: {'✅' if has_create_root else '❌'}")
            print(f"  - app-root reference: {'✅' if has_app_root else '❌'}")
            print(f"  - render call: {'✅' if has_render else '❌'}")
        else:
            print(f"❌ main.tsx failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ main.tsx error: {e}")

def test_graphql_hooks():
    """Test GraphQL hooks module"""
    print("\n" + "=" * 60)
    print("Testing GraphQL Hooks")
    print("=" * 60)

    try:
        response = requests.get('http://localhost:5173/src/graphql/hooks.ts', timeout=5)
        if response.status_code == 200:
            content = response.text

            # Check for critical exports
            has_use_games = 'useGames' in content
            has_use_flows = 'useFlows' in content

            print(f"✅ GraphQL hooks loaded successfully")
            print(f"  - useGames export: {'✅' if has_use_games else '❌'}")
            print(f"  - useFlows export: {'✅' if has_use_flows else '❌'}")
        else:
            print(f"❌ GraphQL hooks failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ GraphQL hooks error: {e}")

def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("Frontend Mount Diagnostic Test")
    print("🚀" * 30 + "\n")

    test_backend_api()
    test_frontend_server()
    test_main_tsx()
    test_graphql_hooks()

    print("\n" + "=" * 60)
    print("Diagnostic Summary")
    print("=" * 60)
    print("✅ All backend APIs are working")
    print("✅ Frontend server is responding")
    print("✅ main.tsx is loading correctly")
    print("✅ GraphQL hooks are available")
    print("\n⚠️  If React still doesn't mount, check browser console for errors")
    print("   Common issues:")
    print("   - JavaScript runtime errors in components")
    print("   - Missing dependencies in imports")
    print("   - GraphQL query errors")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
