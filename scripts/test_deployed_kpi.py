#!/usr/bin/env python3
"""
Test IntelAI deployed service with KPI queries and health scores
Tests the health score and KPI query endpoints
"""
import httpx
import json

# Deployed service URL
INTELAI_URL = "https://intelai.ysiddo-ai-projects.app"

def test_health():
    """Test health endpoint"""
    print("Testing IntelAI Health...")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{INTELAI_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Health Check: {result.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health Check Failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_health_score():
    """Test health score endpoint"""
    print("\nTesting Health Score...")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            # Test HR health score endpoint
            response = client.get(f"{INTELAI_URL}/api/v1/hr/health-score")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Health Score: {result}")
                return True
            else:
                print(f"❌ Health Score Failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health Score Error: {e}")
        return False

def test_kpi_query():
    """Test KPI query via chat endpoint"""
    print("\nTesting KPI Query via Chat...")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            # Test a simple KPI query via chat
            query_data = {
                "message": "What is the current HR workforce summary?",
                "persona": "hr_analyst"
            }
            
            response = client.post(f"{INTELAI_URL}/api/v1/chat", json=query_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ KPI Query: {result.get('response', 'no response')}")
                return True
            else:
                print(f"❌ KPI Query Failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ KPI Query Error: {e}")
        return False

def test_available_kpis():
    """Test available KPIs endpoint"""
    print("\nTesting Available KPIs...")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{INTELAI_URL}/api/v1/kpis")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Available KPIs: {result}")
                return True
            else:
                print(f"❌ Available KPIs Failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Available KPIs Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IntelAI Testing Against Deployed Service")
    print("=" * 60)
    
    results = {
        "Health Check": test_health(),
        "HR Health Score": test_health_score(),
        "KPI Query via Chat": test_kpi_query(),
        "Available KPIs": test_available_kpis()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print("=" * 60)