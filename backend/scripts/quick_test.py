#!/usr/bin/env python
"""Quick API test runner - tests endpoints with sample data."""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from fastapi.testclient import TestClient
    from app.main import app
    
    print("✅ Successfully imported FastAPI and app")
    
    # Create test client
    client = TestClient(app)
    
    # Test 1: Health endpoint
    print("\n🔍 Testing Health Endpoint...")
    response = client.get("/api/v1/health")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ API Status: {data['status']}")
        print(f"   ✓ Version: {data['version']}")
    
    # Test 2: Root endpoint
    print("\n🔍 Testing Root Endpoint...")
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Response: {response.json()['name']}")
    
    # Test 3: List commodities (may be empty)
    print("\n🔍 Testing Commodities Endpoint...")
    response = client.get("/api/v1/market-data/commodities")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        commodities = response.json()
        print(f"   ✓ Found {len(commodities)} commodities")
    
    # Test 4: List markets (may be empty)
    print("\n🔍 Testing Markets Endpoint...")
    response = client.get("/api/v1/market-data/markets")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        markets = response.json()
        print(f"   ✓ Found {len(markets)} markets")
    
    # Test 5: Scheduler status
    print("\n🔍 Testing Scheduler Endpoint...")
    response = client.get("/api/v1/scheduler/status")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Scheduler: {data['status']}")
        print(f"   ✓ Jobs: {len(data['scheduled_jobs'])}")
    
    print("\n" + "=" * 60)
    print("✅ Basic API tests completed successfully!")
    print("=" * 60)
    print("\n📚 API Documentation available at:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("   • Documentation: API_DOCUMENTATION.md")
    print("\n💡 To test with data, run:")
    print("   python scripts/seed_data.py")
    print("   python scripts/test_all_endpoints.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n💡 Install dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
