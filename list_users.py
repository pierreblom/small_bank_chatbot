#!/usr/bin/env python3
"""
List all available users for login
"""
import csv
import hashlib

def list_all_users():
    print("🔐 Available Login Users")
    print("=" * 50)
    
    # Hardcoded users
    print("\n📋 System Users (Hardcoded):")
    print("-" * 30)
    hardcoded_users = {
        "admin": {"password": "admin123", "role": "admin", "name": "Administrator"},
        "banker": {"password": "banker123", "role": "banker", "name": "Bank Representative"},
        "demo": {"password": "demo123", "role": "user", "name": "Demo User"}
    }
    
    for username, data in hardcoded_users.items():
        print(f"👤 {data['name']}")
        print(f"   Username: {username}")
        print(f"   Password: {data['password']}")
        print(f"   Role: {data['role']}")
        print()
    
    # CSV customers
    print("\n👥 Customer Users (from CSV):")
    print("-" * 30)
    try:
        with open('banking_customers.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            customers = list(reader)
            
        print(f"Total customers: {len(customers)}")
        print("\nFirst 10 customers:")
        for i, customer in enumerate(customers[:10]):
            print(f"{i+1}. {customer['first_name']} {customer['last_name']}")
            print(f"   Username: {customer['username']}")
            print(f"   Password: {customer['password_hash']}")
            print(f"   Account: {customer['account_type']}")
            print(f"   Balance: ${float(customer['balance']):,.2f}")
            print()
            
        if len(customers) > 10:
            print(f"... and {len(customers) - 10} more customers")
            
    except FileNotFoundError:
        print("❌ banking_customers.csv not found")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
    
    print("\n💡 Login Instructions:")
    print("-" * 30)
    print("1. Start the server: python app.py")
    print("2. Open http://localhost:5001 in your browser")
    print("3. Use any of the credentials above to login")
    print("4. For customers, use the password_hash as the password")
    
    print("\n🎯 New Customer-Specific Features:")
    print("-" * 30)
    print("• My Profile: Shows your personal account information")
    print("• My Loan: Displays your loan details (if applicable)")
    print("• Personalized AI: Chat assistant knows your account details")
    print("• Customer-specific responses based on your data")
    print("• All data is fictional and for demonstration only")

if __name__ == "__main__":
    list_all_users() 