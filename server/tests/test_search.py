#!/usr/bin/env python3
"""Test script for Phase 2 search functionality."""

import requests
import sys

def test_search():
    """Test the search endpoint."""
    base_url = "http://127.0.0.1:8001"
    
    # Test 1: Search in chat names
    print("Test 1: Search in chat names")
    response = requests.get(f"{base_url}/api/v1/search?q=repository&search_messages=false")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    results = response.json()
    print(f"  ✓ Found {len(results)} chats with 'repository' in name")
    
    # Test 2: Search in messages (deep search)
    print("Test 2: Search in message content")
    response = requests.get(f"{base_url}/api/v1/search?q=FastAPI&search_messages=true")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    results = response.json()
    print(f"  ✓ Found {len(results)} chats with 'FastAPI' in messages")
    if results:
        total_matches = sum(r.get("match_count", 0) for r in results)
        print(f"  ✓ Total matching messages: {total_matches}")
    
    # Test 3: Search with workspace filter
    print("Test 3: Search with workspace filter")
    response = requests.get(f"{base_url}/api/v1/search?q=check&search_messages=false&workspace=/Users/yifen/Workspace/kimi-chat-history")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    results = response.json()
    print(f"  ✓ Found {len(results)} chats in specific workspace")
    
    # Test 4: No results
    print("Test 4: Search with no matches")
    response = requests.get(f"{base_url}/api/v1/search?q=thisdefinitelydoesnotexist12345&search_messages=true")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    results = response.json()
    assert len(results) == 0, f"Expected 0 results, got {len(results)}"
    print("  ✓ Empty results returned correctly")
    
    print("\n✅ All Phase 2 search tests passed!")

if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get("http://127.0.0.1:8001/api/v1/health", timeout=2)
    except Exception:
        print("❌ Server not running. Start it first with:")
        print("   cd server && python3 -m uvicorn main:app --host 127.0.0.1 --port 8001")
        sys.exit(1)
    
    test_search()
