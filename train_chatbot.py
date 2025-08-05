#!/usr/bin/env python3
"""
Banking Chatbot Training Script
This script helps you train your Ollama model with banking-specific data
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return None

def check_ollama_installed():
    """Check if Ollama is installed and running"""
    print("🔍 Checking Ollama installation...")
    
    # Check if ollama command exists
    result = run_command("which ollama", "Checking Ollama installation")
    if not result:
        print("❌ Ollama not found. Please install Ollama first.")
        return False
    
    # Check if Ollama service is running
    result = run_command("ollama list", "Checking Ollama service")
    if not result:
        print("❌ Ollama service not running. Please start Ollama first.")
        return False
    
    print("✅ Ollama is installed and running")
    return True

def create_banking_model():
    """Create a fine-tuned banking model"""
    print("\n🎯 Creating Banking Assistant Model...")
    
    # Check if Modelfile exists
    if not os.path.exists("Modelfile"):
        print("❌ Modelfile not found. Please create a Modelfile first.")
        return False
    
    # Create the model
    result = run_command("ollama create banking-assistant -f Modelfile", "Creating banking assistant model")
    if not result:
        return False
    
    print("✅ Banking assistant model created successfully!")
    return True

def test_banking_model():
    """Test the trained banking model"""
    print("\n🧪 Testing Banking Assistant Model...")
    
    test_questions = [
        "What is my account balance?",
        "How do I apply for a loan?",
        "What's the difference between APR and APY?",
        "How do I set up online banking?",
        "What should I do if I suspect fraud?"
    ]
    
    for question in test_questions:
        print(f"\n🤔 Question: {question}")
        result = run_command(f'echo "{question}" | ollama run banking-assistant', f"Testing: {question}")
        if result:
            print(f"💬 Response: {result.strip()}")
        else:
            print("❌ No response received")

def show_training_options():
    """Show different training options"""
    print("\n" + "="*60)
    print("🎯 BANKING CHATBOT TRAINING OPTIONS")
    print("="*60)
    
    print("\n1️⃣ **Ollama Fine-tuning (Recommended)**")
    print("   - Uses Modelfile with banking-specific prompts")
    print("   - Includes training data from banking-training-data.txt")
    print("   - Creates a custom 'banking-assistant' model")
    print("   - Best for domain-specific knowledge")
    
    print("\n2️⃣ **Prompt Engineering**")
    print("   - Modify system prompts in BE/app.py")
    print("   - Add customer-specific context")
    print("   - No model retraining required")
    print("   - Quick to implement")
    
    print("\n3️⃣ **RAG (Retrieval-Augmented Generation)**")
    print("   - Add banking knowledge base")
    print("   - Retrieve relevant information during chat")
    print("   - More accurate responses")
    print("   - Requires additional setup")
    
    print("\n4️⃣ **Conversation Memory**")
    print("   - Improve context retention")
    print("   - Better conversation flow")
    print("   - Personalized responses")
    print("   - Already partially implemented")
    
    print("\n5️⃣ **Multi-Model Approach**")
    print("   - Use different models for different tasks")
    print("   - Specialized models for loans, investments, etc.")
    print("   - Higher accuracy for specific domains")
    print("   - More complex setup")

def create_rag_setup():
    """Create RAG (Retrieval-Augmented Generation) setup"""
    print("\n📚 Creating RAG Setup...")
    
    # Create knowledge base directory
    os.makedirs("knowledge_base", exist_ok=True)
    
    # Create sample knowledge base files
    knowledge_files = {
        "loan_products.md": """# Loan Products

## Personal Loans
- Amount: $1,000 - $50,000
- Term: 12-60 months
- Rate: 5.99% - 18.99% APR
- Requirements: 650+ credit score, proof of income

## Auto Loans
- Amount: $5,000 - $75,000
- Term: 24-84 months
- Rate: 3.99% - 12.99% APR
- Requirements: 600+ credit score, vehicle as collateral

## Home Loans
- Amount: $50,000 - $500,000
- Term: 15-30 years
- Rate: 4.5% - 7.5% APR
- Requirements: 680+ credit score, 20% down payment
""",
        
        "account_types.md": """# Account Types

## Checking Accounts
- Basic Checking: $5/month (waived with $500 balance)
- Premium Checking: $12/month (waived with $1,500 balance)
- Student Checking: Free (ages 16-24)
- Senior Checking: Free (ages 65+)

## Savings Accounts
- Basic Savings: $3/month (waived with $300 balance)
- High-Yield Savings: Free (2.5% APY)
- Money Market: $10/month (2.8% APY, check-writing)

## Investment Accounts
- Traditional IRA: Tax-deductible contributions
- Roth IRA: Tax-free withdrawals
- 401(k) Rollover: Transfer from previous employer
- CDs: 3.5% APY for 12-month terms
""",
        
        "security_protocols.md": """# Security Protocols

## Fraud Prevention
- Zero liability for unauthorized transactions
- Real-time fraud monitoring
- Two-factor authentication available
- Biometric login support

## Account Security
- Strong password requirements
- Security questions for recovery
- Account lockout after failed attempts
- Suspicious activity alerts

## Data Protection
- End-to-end encryption
- Regular security audits
- Compliance with banking regulations
- Secure data centers
"""
    }
    
    for filename, content in knowledge_files.items():
        with open(f"knowledge_base/{filename}", "w") as f:
            f.write(content)
        print(f"✅ Created {filename}")
    
    print("✅ RAG knowledge base created!")

def main():
    """Main training script"""
    print("🏦 Banking Chatbot Training Script")
    print("="*40)
    
    # Check Ollama installation
    if not check_ollama_installed():
        return
    
    while True:
        print("\n" + "="*40)
        print("🎯 TRAINING OPTIONS")
        print("="*40)
        print("1. Create Banking Assistant Model (Fine-tuning)")
        print("2. Test Banking Model")
        print("3. Show All Training Options")
        print("4. Create RAG Knowledge Base")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            create_banking_model()
        elif choice == "2":
            test_banking_model()
        elif choice == "3":
            show_training_options()
        elif choice == "4":
            create_rag_setup()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main() 