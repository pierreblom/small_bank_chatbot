#!/usr/bin/env python3
"""
Test script for multi-session functionality
This script tests logging in as both admin and customer simultaneously
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_multi_session():
    """Test multi-session functionality"""
    print("🧪 Testing Multi-Session Functionality")
    print("=" * 50)
    
    # Test data
    admin_credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    customer_credentials = {
        "username": "johnsmith",
        "password": "p"
    }
    
    # Create separate sessions
    admin_session = requests.Session()
    customer_session = requests.Session()
    
    print("1. Testing Admin Login...")
    try:
        admin_response = admin_session.post(
            f"{BASE_URL}/api/auth/login/admin",
            json=admin_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            print(f"✅ Admin login successful: {admin_data['user']['username']}")
        else:
            print(f"❌ Admin login failed: {admin_response.text}")
            return False
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return False
    
    print("\n2. Testing Customer Login...")
    try:
        customer_response = customer_session.post(
            f"{BASE_URL}/api/auth/login/customer",
            json=customer_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        if customer_response.status_code == 200:
            customer_data = customer_response.json()
            print(f"✅ Customer login successful: {customer_data['user']['username']}")
        else:
            print(f"❌ Customer login failed: {customer_response.text}")
            return False
    except Exception as e:
        print(f"❌ Customer login error: {e}")
        return False
    
    print("\n3. Testing Concurrent Session Access...")
    
    # Test admin session access
    try:
        admin_status = admin_session.get(f"{BASE_URL}/api/auth/status")
        if admin_status.status_code == 200:
            admin_status_data = admin_status.json()
            print(f"✅ Admin session active: {admin_status_data['user']['username']} ({admin_status_data['user']['role']})")
        else:
            print(f"❌ Admin session check failed: {admin_status.text}")
    except Exception as e:
        print(f"❌ Admin session check error: {e}")
    
    # Test customer session access
    try:
        customer_status = customer_session.get(f"{BASE_URL}/api/auth/status")
        if customer_status.status_code == 200:
            customer_status_data = customer_status.json()
            print(f"✅ Customer session active: {customer_status_data['user']['username']} ({customer_status_data['user']['role']})")
        else:
            print(f"❌ Customer session check failed: {customer_status.text}")
    except Exception as e:
        print(f"❌ Customer session check error: {e}")
    
    print("\n4. Testing Admin-Only Endpoints...")
    
    # Test admin stats endpoint with admin session
    try:
        admin_stats = admin_session.get(f"{BASE_URL}/api/admin/stats")
        if admin_stats.status_code == 200:
            print("✅ Admin can access admin stats")
        else:
            print(f"❌ Admin cannot access admin stats: {admin_stats.text}")
    except Exception as e:
        print(f"❌ Admin stats error: {e}")
    
    # Test admin stats endpoint with customer session (should fail)
    try:
        customer_admin_stats = customer_session.get(f"{BASE_URL}/api/admin/stats")
        if customer_admin_stats.status_code == 403:
            print("✅ Customer correctly blocked from admin stats")
        else:
            print(f"❌ Customer should be blocked from admin stats: {customer_admin_stats.text}")
    except Exception as e:
        print(f"❌ Customer admin stats test error: {e}")
    
    print("\n5. Testing Logout...")
    
    # Logout admin
    try:
        admin_logout = admin_session.post(f"{BASE_URL}/api/auth/logout")
        if admin_logout.status_code == 200:
            print("✅ Admin logout successful")
        else:
            print(f"❌ Admin logout failed: {admin_logout.text}")
    except Exception as e:
        print(f"❌ Admin logout error: {e}")
    
    # Logout customer
    try:
        customer_logout = customer_session.post(f"{BASE_URL}/api/auth/logout")
        if customer_logout.status_code == 200:
            print("✅ Customer logout successful")
        else:
            print(f"❌ Customer logout failed: {customer_logout.text}")
    except Exception as e:
        print(f"❌ Customer logout error: {e}")
    
    print("\n6. Verifying Sessions are Cleared...")
    
    # Check admin session is cleared
    try:
        admin_status_after = admin_session.get(f"{BASE_URL}/api/auth/status")
        if admin_status_after.status_code == 200:
            admin_status_data_after = admin_status_after.json()
            if not admin_status_data_after.get('authenticated', True):
                print("✅ Admin session properly cleared")
            else:
                print("❌ Admin session not cleared")
        else:
            print("✅ Admin session cleared (401 response)")
    except Exception as e:
        print(f"❌ Admin session check error: {e}")
    
    # Check customer session is cleared
    try:
        customer_status_after = customer_session.get(f"{BASE_URL}/api/auth/status")
        if customer_status_after.status_code == 200:
            customer_status_data_after = customer_status_after.json()
            if not customer_status_data_after.get('authenticated', True):
                print("✅ Customer session properly cleared")
            else:
                print("❌ Customer session not cleared")
        else:
            print("✅ Customer session cleared (401 response)")
    except Exception as e:
        print(f"❌ Customer session check error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Multi-session test completed!")
    print("\nTo test manually:")
    print("1. Open http://localhost:5001 in your browser")
    print("2. Click 'Admin Login' and login as admin")
    print("3. Open a new tab and go to http://localhost:5001")
    print("4. Click 'Customer Login' and login as customer")
    print("5. You should now have both sessions active in different tabs!")
    
    return True

if __name__ == "__main__":
    test_multi_session() 