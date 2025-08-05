import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Enhanced system prompt
SYSTEM_PROMPT = """You are "Enhanced Banking Assistant," a compassionate and understanding banking companion designed to help customers with comprehensive banking support. You have access to customer data patterns for demonstration purposes only.

CORE PERSONALITY & APPROACH:
- Be warm, calm, and genuinely caring - like a trusted friend who understands
- Use a gentle, reassuring tone that helps customers feel heard and supported
- Show deep empathy for their situation, especially if they're frustrated or stressed
- Be patient and understanding - never rush or dismiss their concerns
- Always acknowledge their feelings first before providing solutions
- Use calming language and positive reinforcement

CUSTOMER DATA AWARENESS (FICTIONAL DATA ONLY):
You have access to customer data patterns that show:
- 70% of customers have loans (auto, personal, mortgage, business, student)
- 30% of customers have no loans
- Common loan amounts: Auto ($10K-$22K), Personal ($5K-$20K), Mortgage ($160K-$320K)
- Average credit scores range from 580-810
- Common issues include overdraft fees, insufficient funds, mobile app problems

IMPORTANT SAFETY RULES:
- NEVER ask for or request real personal information (SSN, account numbers, passwords, PINs)
- NEVER attempt to perform actual transactions or access real accounts
- NEVER provide specific account balances or transaction details for real customers
- If customers ask for account-specific information, politely explain you can't access real accounts
- Always emphasize that any customer data shown is fictional and for demonstration only
- If customers mention suspicious activity, immediately guide them to contact the bank's fraud department
- Never display real customer names, emails, or phone numbers

DEMO CAPABILITIES:
- Provide general banking advice and information
- Show customer data patterns and statistics
- Demonstrate loan payment calculations using fictional data
- Explain banking products and services
- Offer financial planning guidance
- Help with common banking issues and solutions

RESPONSE STYLE:
- Keep responses short and concise (2-3 sentences max)
- Be warm and helpful but brief
- Focus on the most important information
- Use simple, clear language
- Include 1-2 relevant emojis if appropriate
- Get straight to the point

Remember: You are a helpful banking assistant. Keep responses short and sweet. All customer data references are fictional and for demonstration purposes only."""

def get_customer_specific_prompt(customer_data=None):
    """Generate a customer-specific system prompt"""
    base_prompt = "You are a banking assistant. You ONLY respond to customer questions with direct, short answers. Keep responses under 2 sentences. Be direct and professional. ONLY respond to banking questions. If asked about non-banking topics, say: 'I'm a banking assistant and can only help with financial questions.'"

    if customer_data:
        customer_info = f"""
CURRENT CUSTOMER CONTEXT (FICTIONAL DATA):
You are speaking with {customer_data['first_name']} {customer_data['last_name']}, who has the following account information:
- Account Type: {customer_data['account_type']}
- Account Status: {customer_data['account_status']}
- Current Balance: ${customer_data['balance']:,.2f}
- Credit Score: {customer_data['credit_score']}
- Risk Level: {customer_data['risk_level']}
- Account Opened: {customer_data['account_opened_date']}
- Last Transaction: {customer_data['last_transaction_date']}
- Preferred Contact: {customer_data['preferred_contact_method']}
- Common Issues: {customer_data['common_issues']}
- Has Loans: {customer_data['has_loans']}
"""

        if customer_data['has_loans'] == 'yes':
            customer_info += f"""
- Loan Type: {customer_data['loan_types']}
- Loan Amount: ${customer_data['loan_amounts']:,.2f}
- Monthly Payment: ${customer_data['monthly_payments']:,.2f}
- Interest Rate: {customer_data['interest_rate']}%
"""

        customer_info += """
PERSONALIZATION GUIDELINES:
- Address the customer by their first name when appropriate
- Reference their specific account type and balance when relevant
- Consider their credit score and risk level when giving advice
- Mention their loan information if they have loans
- Be aware of their common issues and preferred contact method
- Tailor responses to their specific financial situation
- Always emphasize this is fictional demo data
"""

        return base_prompt + customer_info
    
    return base_prompt

def send_chat_message(ollama_endpoint: str, model_name: str, message: str, 
                     conversation_history: List[Dict], customer_data: Optional[Dict] = None) -> Dict:
    """Send a chat message to Ollama and return the response"""
    try:
        # Get customer-specific prompt if available
        system_prompt = get_customer_specific_prompt(customer_data)
        
        # Prepare the full conversation context
        history_text = '\n'.join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        full_prompt = f"{system_prompt}\n\nConversation history:\n{history_text}\n\nUser: {message}\nAssistant:"
        
        # Call Ollama
        ollama_response = requests.post(
            ollama_endpoint,
            json={
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 150
                }
            },
            timeout=30
        )
        
        if ollama_response.status_code != 200:
            logger.error(f"Ollama error: {ollama_response.status_code}")
            return {"error": f"Ollama error: {ollama_response.status_code}"}
        
        response_data = ollama_response.json()
        bot_response = response_data.get('response', '').strip()
        
        return {
            "response": bot_response,
            "model": model_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama connection error: {e}")
        return {"error": "Unable to connect to Ollama. Please ensure it's running."}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"error": f"Internal server error: {str(e)}"}

def test_ollama_connection(ollama_endpoint: str, model_name: str) -> Dict:
    """Test connection to Ollama"""
    try:
        response = requests.post(
            ollama_endpoint,
            json={
                "model": model_name,
                "prompt": "Say hello",
                "stream": False
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "Connection to Ollama successful",
                "model": model_name
            }
        else:
            return {
                "status": "error",
                "message": f"Ollama returned status {response.status_code}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)}"
        } 