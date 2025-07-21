from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
from flask_cors import CORS
import requests
import json
import csv
import os
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional
import logging
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Use a consistent secret key for session management
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Session expires in 24 hours
CORS(app, 
     supports_credentials=True,  # Enable CORS with credentials
     origins=["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:5001", "http://127.0.0.1:5001"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configuration
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"
CSV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "banking_customers.csv")

# User database (in production, this would be a real database)
# Keep the hardcoded users as fallback
USERS = {
    "admin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "name": "Administrator"
    },
    "banker": {
        "password": hashlib.sha256("banker123".encode()).hexdigest(),
        "role": "banker",
        "name": "Bank Representative"
    },
    "demo": {
        "password": hashlib.sha256("demo123".encode()).hexdigest(),
        "role": "user",
        "name": "Demo User"
    }
}

# Load customer data from CSV
def load_customer_data() -> List[Dict]:
    """Load customer data from CSV file"""
    customers = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric fields
                row['balance'] = float(row['balance'])
                row['credit_score'] = int(row['credit_score'])
                row['loan_amounts'] = float(row['loan_amounts'])
                row['monthly_payments'] = float(row['monthly_payments'])
                customers.append(row)
        logger.info(f"Loaded {len(customers)} customers from CSV")
        return customers
    except FileNotFoundError:
        logger.error(f"CSV file {CSV_FILE} not found")
        return []
    except Exception as e:
        logger.error(f"Error loading customer data: {e}")
        return []

def validate_customer_login(username: str, password: str) -> Optional[Dict]:
    """Validate customer login using CSV data"""
    customers = load_customer_data()
    
    for customer in customers:
        if customer['username'] == username:
            # Hash the input password and compare with stored hash
            # For demo purposes, we'll use a simple approach
            # In production, you'd use proper password hashing like bcrypt
            hashed_input = hashlib.sha256(password.encode()).hexdigest()
            
            # For demo, we'll also accept the password directly if it matches a pattern
            # This allows using the password_hash from CSV as the password
            if customer['password_hash'] == hashed_input or customer['password_hash'] == password:
                # Determine role based on account_type
                role = "admin" if customer['account_type'] == 'admin' else "customer"
                
                return {
                    "username": customer['username'],
                    "role": role,
                    "name": f"{customer['first_name']} {customer['last_name']}",
                    "customer_data": customer
                }
    return None

def get_customer_by_username(username: str) -> Optional[Dict]:
    """Get customer data by username"""
    customers = load_customer_data()
    for customer in customers:
        if customer['username'] == username:
            return customer
    return None

def update_customer_password(username: str, new_password: str) -> bool:
    """Update customer password in CSV"""
    try:
        # Read all customers
        customers = []
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    # Update password hash
                    row['password_hash'] = hashlib.sha256(new_password.encode()).hexdigest()
                    # Clear reset token
                    row['reset_token'] = ''
                    row['reset_token_expiry'] = ''
                customers.append(row)
        
        # Write back to CSV
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            if customers:
                fieldnames = customers[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(customers)
        
        logger.info(f"Password updated for user {username}")
        return True
    except Exception as e:
        logger.error(f"Error updating password for {username}: {e}")
        return False

def generate_reset_token(username: str) -> Optional[str]:
    """Generate a password reset token for a user"""
    try:
        # Read all customers
        customers = []
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    # Generate reset token and expiry
                    reset_token = str(uuid.uuid4())
                    expiry = (datetime.now() + timedelta(hours=1)).isoformat()
                    row['reset_token'] = reset_token
                    row['reset_token_expiry'] = expiry
                customers.append(row)
        
        # Write back to CSV
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            if customers:
                fieldnames = customers[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(customers)
        
        logger.info(f"Reset token generated for user {username}")
        return reset_token
    except Exception as e:
        logger.error(f"Error generating reset token for {username}: {e}")
        return None

def validate_reset_token(username: str, token: str) -> bool:
    """Validate a password reset token"""
    customer = get_customer_by_username(username)
    if not customer:
        return False
    
    if not customer.get('reset_token') or not customer.get('reset_token_expiry'):
        return False
    
    if customer['reset_token'] != token:
        return False
    
    try:
        expiry = datetime.fromisoformat(customer['reset_token_expiry'])
        if datetime.now() > expiry:
            return False
    except:
        return False
    
    return True

# Authentication decorator
def login_required(f):
    """Decorator to require login for protected routes"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

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

# Customer-specific system prompt
def get_customer_specific_prompt(customer_data=None):
    """Generate a customer-specific system prompt"""
    base_prompt = """You are "Enhanced Banking Assistant," a compassionate and understanding banking companion designed to help customers with comprehensive banking support. You have access to customer data patterns for demonstration purposes only.

CORE PERSONALITY & APPROACH:
- Be warm, calm, and genuinely caring - like a trusted friend who understands
- Use a gentle, reassuring tone that helps customers feel heard and supported
- Show deep empathy for their situation, especially if they're frustrated or stressed
- Be patient and understanding - never rush or dismiss their concerns
- Always acknowledge their feelings first before providing solutions
- Use calming language and positive reinforcement

IMPORTANT SAFETY RULES:
- NEVER ask for or request real personal information (SSN, account numbers, passwords, PINs)
- NEVER attempt to perform actual transactions or access real accounts
- NEVER provide specific account balances or transaction details for real customers
- If customers ask for account-specific information, politely explain you can't access real accounts
- Always emphasize that any customer data shown is fictional and for demonstration only
- If customers mention suspicious activity, immediately guide them to contact the bank's fraud department
- Never display real customer names, emails, or phone numbers

RESPONSE STYLE:
- Keep responses short and concise (2-3 sentences max)
- Be warm and helpful but brief
- Focus on the most important information
- Use simple, clear language
- Include 1-2 relevant emojis if appropriate
- Get straight to the point

Remember: You are a helpful banking assistant. Keep responses short and sweet. All customer data references are fictional and for demonstration purposes only."""

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

class BankingAssistant:
    def __init__(self):
        self.customers = load_customer_data()
        self.conversation_history = []
        
    def get_customer_stats(self) -> Dict:
        """Get comprehensive customer statistics"""
        if not self.customers:
            return {"error": "No customer data available"}
            
        total_customers = len(self.customers)
        customers_with_loans = len([c for c in self.customers if c['has_loans'] == 'yes'])
        customers_without_loans = total_customers - customers_with_loans
        
        # Loan type distribution
        loan_types = {}
        for customer in self.customers:
            if customer['has_loans'] == 'yes' and customer['loan_types'] != 'none':
                loan_type = customer['loan_types']
                loan_types[loan_type] = loan_types.get(loan_type, 0) + 1
        
        # Account type distribution
        account_types = {}
        for customer in self.customers:
            account_type = customer['account_type']
            account_types[account_type] = account_types.get(account_type, 0) + 1
        
        # Risk level distribution
        risk_levels = {}
        for customer in self.customers:
            risk_level = customer['risk_level']
            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        # Calculate averages
        avg_credit_score = round(sum(c['credit_score'] for c in self.customers) / total_customers)
        avg_balance = round(sum(c['balance'] for c in self.customers) / total_customers, 2)
        avg_loan_amount = round(sum(c['loan_amounts'] for c in self.customers if c['has_loans'] == 'yes') / customers_with_loans, 2) if customers_with_loans > 0 else 0
        
        return {
            "total_customers": total_customers,
            "customers_with_loans": customers_with_loans,
            "customers_without_loans": customers_without_loans,
            "loan_percentage": round(customers_with_loans / total_customers * 100, 1),
            "loan_types": loan_types,
            "account_types": account_types,
            "risk_levels": risk_levels,
            "average_credit_score": avg_credit_score,
            "average_balance": avg_balance,
            "average_loan_amount": avg_loan_amount
        }
    
    def get_random_customer(self) -> Dict:
        """Get a random customer profile"""
        if not self.customers:
            return {"error": "No customer data available"}
        return random.choice(self.customers)
    
    def search_customers(self, query: str) -> List[Dict]:
        """Search customers by various criteria"""
        if not self.customers:
            return []
            
        query = query.lower()
        results = []
        
        for customer in self.customers:
            # Search in name, email, account type, loan type, common issues
            searchable_fields = [
                customer['first_name'].lower(),
                customer['last_name'].lower(),
                customer['email'].lower(),
                customer['account_type'].lower(),
                customer['loan_types'].lower(),
                customer['common_issues'].lower(),
                customer['risk_level'].lower()
            ]
            
            if any(query in field for field in searchable_fields):
                results.append(customer)
                
        return results[:10]  # Limit to 10 results
    
    def get_customers_by_loan_type(self, loan_type: str) -> List[Dict]:
        """Get customers by loan type"""
        if not self.customers:
            return []
            
        return [c for c in self.customers if c['loan_types'] == loan_type]
    
    def get_customers_by_risk_level(self, risk_level: str) -> List[Dict]:
        """Get customers by risk level"""
        if not self.customers:
            return []
            
        return [c for c in self.customers if c['risk_level'] == risk_level]
    
    def calculate_loan_payment(self, principal: float, rate: float, years: int) -> Dict:
        """Calculate loan payment using simple interest formula"""
        monthly_rate = rate / 12 / 100
        num_payments = years * 12
        
        if monthly_rate == 0:
            monthly_payment = principal / num_payments
        else:
            monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
        
        total_payment = monthly_payment * num_payments
        total_interest = total_payment - principal
        
        return {
            "principal": principal,
            "annual_rate": rate,
            "years": years,
            "monthly_payment": round(monthly_payment, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2)
        }

# Initialize banking assistant
banking_assistant = BankingAssistant()

@app.route('/')
def index():
    """Serve the main index page"""
    try:
        index_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "index.html")
        return send_file(index_file_path, mimetype='text/html')
    except FileNotFoundError:
        return "Index page not found", 404

@app.route('/login.html')
def login_page():
    """Serve the login page"""
    try:
        login_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "login.html")
        return send_file(login_file_path, mimetype='text/html')
    except FileNotFoundError:
        return "Login page not found", 404

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images from the FE/images directory"""
    try:
        image_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "images", filename)
        return send_file(image_file_path)
    except FileNotFoundError:
        return "Image not found", 404

@app.route('/css/<filename>')
def serve_css(filename):
    """Serve CSS files from the FE/css directory"""
    try:
        css_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "css", filename)
        return send_file(css_file_path, mimetype='text/css')
    except FileNotFoundError:
        return "CSS file not found", 404

@app.route('/js/<filename>')
def serve_js(filename):
    """Serve JavaScript files from the FE/js directory"""
    try:
        js_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "js", filename)
        return send_file(js_file_path, mimetype='application/javascript')
    except FileNotFoundError:
        return "JavaScript file not found", 404

@app.route('/Gemini_Generated_Image_b2kiqjb2kiqjb2ki.png')
def serve_bank_logo():
    """Serve the bank logo image"""
    try:
        logo_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "images", "Gemini_Generated_Image_b2kiqjb2kiqjb2ki.png")
        return send_file(logo_file_path, mimetype='image/png')
    except FileNotFoundError:
        return "Logo not found", 404

@app.route('/loan-calculator.html')
@login_required
def loan_calculator():
    """Serve the loan calculator page"""
    try:
        loan_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "loan-calculator.html")
        return send_file(loan_file_path, mimetype='text/html')
    except FileNotFoundError:
        return "Loan calculator not found", 404

@app.route('/chat')
@login_required
def chat_page():
    """Serve the chat page (requires authentication)"""
    try:
        chat_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "small-bank-chat-backend.html")
        return send_file(chat_file_path, mimetype='text/html')
    except FileNotFoundError:
        return "Chat page not found", 404

@app.route('/admin')
@login_required
def admin_page():
    """Serve the admin dashboard page (requires admin authentication)"""
    # Check if user is admin
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    user_role = session.get('user_role')
    
    # Check if user is admin (either from hardcoded users or CSV)
    if user_role != 'admin':
        return redirect('/chat')
    
    try:
        admin_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "admin_dashboard.html")
        return send_file(admin_file_path, mimetype='text/html')
    except FileNotFoundError:
        return "Admin dashboard not found", 404

@app.route('/admin_dashboard.html')
@login_required
def admin_dashboard_page():
    """Serve the admin dashboard page"""
    try:
        admin_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "FE", "admin_dashboard.html")
        return send_file(admin_file_path, mimetype='text/html')
    except FileNotFoundError:
        return "Admin dashboard not found", 404

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        # First check hardcoded users (admin, banker, demo)
        if username in USERS:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if USERS[username]['password'] == hashed_password:
                # Store user info in session
                session['user_id'] = username
                session['user_role'] = USERS[username]['role']
                session['user_name'] = USERS[username]['name']
                
                logger.info(f"User {username} logged in successfully")
                logger.info(f"Session after login: {dict(session)}")
                
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "username": username,
                        "role": USERS[username]['role'],
                        "name": USERS[username]['name']
                    }
                })
        
        # Then check customer login from CSV
        customer_user = validate_customer_login(username, password)
        if customer_user:
            session['user_id'] = customer_user['username']
            session['user_role'] = customer_user['role']
            session['user_name'] = customer_user['name']
            session['customer_data'] = customer_user['customer_data']  # Store customer data in session
            logger.info(f"Customer {username} logged in successfully")
            logger.info(f"Session after customer login: {dict(session)}")
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "username": username,
                    "role": customer_user['role'],
                    "name": customer_user['name']
                }
            })
        
        return jsonify({"error": "Invalid username or password"}), 401
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    logger.info(f"Logout request - Session before: {dict(session)}")
    
    # Clear all session data
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    session.pop('customer_data', None)
    session.clear()
    
    logger.info(f"Logout completed - Session after: {dict(session)}")
    
    # Create response and set session cookie to expire immediately
    response = jsonify({"success": True, "message": "Logout successful"})
    response.delete_cookie('session')
    response.set_cookie('session', '', expires=0, max_age=0)
    
    # Force session to be marked as modified
    session.modified = True
    
    return response

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Get current authentication status"""
    logger.info(f"Auth status check - Session: {dict(session)}")
    if 'user_id' in session:
        logger.info(f"User {session['user_id']} is authenticated")
        return jsonify({
            "authenticated": True,
            "user": {
                "username": session['user_id'],
                "role": session.get('user_role'),
                "name": session.get('user_name')
            }
        })
    else:
        logger.info("No user_id in session - not authenticated")
        return jsonify({"authenticated": False})

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Handle forgot password request"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        # Check if user exists
        customer = get_customer_by_username(username)
        if not customer:
            # Don't reveal if user exists or not for security
            return jsonify({
                "success": True,
                "message": "If the username exists, a reset link has been sent."
            })
        
        # Generate reset token
        reset_token = generate_reset_token(username)
        if not reset_token:
            return jsonify({"error": "Failed to generate reset token"}), 500
        
        # In a real application, you would send an email here
        # For demo purposes, we'll return the token in the response
        return jsonify({
            "success": True,
            "message": "Password reset instructions sent.",
            "reset_token": reset_token,  # Remove this in production
            "username": username  # Remove this in production
        })
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return jsonify({"error": "Password reset failed"}), 500

@app.route('/api/auth/verify-security-question', methods=['POST'])
def verify_security_question():
    """Verify security question answer"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        answer = data.get('answer', '').strip()
        
        if not username or not answer:
            return jsonify({"error": "Username and answer are required"}), 400
        
        customer = get_customer_by_username(username)
        if not customer:
            return jsonify({"error": "User not found"}), 404
        
        # Check security answer (case-insensitive)
        if customer.get('security_answer', '').lower() == answer.lower():
            return jsonify({
                "success": True,
                "message": "Security question verified",
                "security_question": customer.get('security_question', '')
            })
        else:
            return jsonify({"error": "Incorrect answer"}), 401
        
    except Exception as e:
        logger.error(f"Security question verification error: {e}")
        return jsonify({"error": "Verification failed"}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '').strip()
        
        if not username or not token or not new_password:
            return jsonify({"error": "Username, token, and new password are required"}), 400
        
        if len(new_password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        # Validate token
        if not validate_reset_token(username, token):
            return jsonify({"error": "Invalid or expired reset token"}), 401
        
        # Update password
        if update_customer_password(username, new_password):
            return jsonify({
                "success": True,
                "message": "Password reset successfully"
            })
        else:
            return jsonify({"error": "Failed to update password"}), 500
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({"error": "Password reset failed"}), 500

@app.route('/api/auth/get-security-question', methods=['GET'])
def get_security_question():
    """Get security question for a username"""
    try:
        username = request.args.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        customer = get_customer_by_username(username)
        if not customer:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "security_question": customer.get('security_question', '')
        })
        
    except Exception as e:
        logger.error(f"Get security question error: {e}")
        return jsonify({"error": "Failed to get security question"}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat messages with Ollama"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        conversation_history = data.get('history', [])
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get customer-specific prompt if available
        customer_data = session.get('customer_data')
        system_prompt = get_customer_specific_prompt(customer_data)
        
        # Prepare the full conversation context
        history_text = '\n'.join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        full_prompt = f"{system_prompt}\n\nConversation history:\n{history_text}\n\nUser: {message}\nAssistant:"
        
        # Call Ollama
        ollama_response = requests.post(
            OLLAMA_ENDPOINT,
            json={
                "model": MODEL_NAME,
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
            return jsonify({"error": f"Ollama error: {ollama_response.status_code}"}), 500
        
        response_data = ollama_response.json()
        bot_response = response_data.get('response', '').strip()
        
        return jsonify({
            "response": bot_response,
            "model": MODEL_NAME,
            "timestamp": datetime.now().isoformat()
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama connection error: {e}")
        return jsonify({"error": "Unable to connect to Ollama. Please ensure it's running."}), 503
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/test-connection', methods=['GET'])
@login_required
def test_connection():
    """Test Ollama connection"""
    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            json={
                "model": MODEL_NAME,
                "prompt": "Say hello",
                "stream": False
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "message": "Connection to Ollama successful",
                "model": MODEL_NAME
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Ollama returned status {response.status_code}"
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Connection failed: {str(e)}"
        }), 503

@app.route('/api/customer/current', methods=['GET'])
@login_required
def get_current_customer():
    """Get the current logged-in customer's profile"""
    if 'customer_data' in session:
        return jsonify(session['customer_data'])
    else:
        # Fallback for non-customer users (admin, banker, demo)
        customer = banking_assistant.get_random_customer()
        return jsonify(customer)

@app.route('/api/customer/random', methods=['GET'])
@login_required
def get_random_customer():
    """Get a random customer profile"""
    customer = banking_assistant.get_random_customer()
    return jsonify(customer)

@app.route('/api/customer/search', methods=['GET'])
@login_required
def search_customers():
    """Search customers"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    results = banking_assistant.search_customers(query)
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results)
    })

@app.route('/api/customer/stats', methods=['GET'])
@login_required
def get_customer_stats():
    """Get customer statistics"""
    stats = banking_assistant.get_customer_stats()
    return jsonify(stats)

@app.route('/api/customer/loan-type/<loan_type>', methods=['GET'])
@login_required
def get_customers_by_loan_type(loan_type):
    """Get customers by loan type"""
    customers = banking_assistant.get_customers_by_loan_type(loan_type)
    return jsonify({
        "loan_type": loan_type,
        "customers": customers,
        "count": len(customers)
    })

@app.route('/api/customer/risk-level/<risk_level>', methods=['GET'])
@login_required
def get_customers_by_risk_level(risk_level):
    """Get customers by risk level"""
    customers = banking_assistant.get_customers_by_risk_level(risk_level)
    return jsonify({
        "risk_level": risk_level,
        "customers": customers,
        "count": len(customers)
    })

@app.route('/api/loan/calculate', methods=['POST'])
@login_required
def calculate_loan():
    """Calculate loan payment"""
    try:
        data = request.get_json()
        principal = float(data.get('principal', 0))
        rate = float(data.get('rate', 0))
        years = int(data.get('years', 0))
        
        if principal <= 0 or rate < 0 or years <= 0:
            return jsonify({"error": "Invalid loan parameters"}), 400
        
        result = banking_assistant.calculate_loan_payment(principal, rate, years)
        return jsonify(result)
        
    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid input parameters"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500

@app.route('/api/customer/my-loan', methods=['GET'])
@login_required
def get_my_loan():
    """Get current customer's loan information"""
    if 'customer_data' in session:
        customer = session['customer_data']
        if customer['has_loans'] == 'yes':
            return jsonify({
                "has_loan": True,
                "loan_type": customer['loan_types'],
                "loan_amount": customer['loan_amounts'],
                "monthly_payment": customer['monthly_payments'],
                "interest_rate": customer['interest_rate']
            })
        else:
            return jsonify({
                "has_loan": False,
                "message": "You don't have any active loans"
            })
    else:
        return jsonify({"error": "No customer data available"}), 400

@app.route('/api/customer/my-account', methods=['GET'])
@login_required
def get_my_account():
    """Get current customer's account summary"""
    if 'customer_data' in session:
        customer = session['customer_data']
        return jsonify({
            "name": f"{customer['first_name']} {customer['last_name']}",
            "account_type": customer['account_type'],
            "account_status": customer['account_status'],
            "balance": customer['balance'],
            "credit_score": customer['credit_score'],
            "risk_level": customer['risk_level'],
            "account_opened_date": customer['account_opened_date'],
            "last_transaction_date": customer['last_transaction_date'],
            "preferred_contact_method": customer['preferred_contact_method'],
            "common_issues": customer['common_issues'],
            "has_loans": customer['has_loans'],
            "loan_types": customer['loan_types'] if customer['has_loans'] == 'yes' else None,
            "loan_amounts": customer['loan_amounts'] if customer['has_loans'] == 'yes' else None,
            "monthly_payments": customer['monthly_payments'] if customer['has_loans'] == 'yes' else None,
            "interest_rate": customer['interest_rate']
        })
    else:
        return jsonify({"error": "No customer data available"}), 400

# Admin decorator
def admin_required(f):
    """Decorator to require admin privileges"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('user_role')
        if user_role != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/admin/customers', methods=['GET'])
@admin_required
def get_all_customers():
    """Get all customer data (admin only)"""
    try:
        customers = load_customer_data()
        return jsonify({
            "customers": customers,
            "count": len(customers),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error loading customer data: {e}")
        return jsonify({"error": "Failed to load customer data"}), 500

@app.route('/api/admin/customer/<customer_id>', methods=['GET'])
@admin_required
def get_customer_by_id(customer_id):
    """Get specific customer by ID (admin only)"""
    try:
        customers = load_customer_data()
        customer = next((c for c in customers if c['customer_id'] == customer_id), None)
        
        if customer:
            return jsonify(customer)
        else:
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        logger.error(f"Error loading customer data: {e}")
        return jsonify({"error": "Failed to load customer data"}), 500

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Get comprehensive admin statistics"""
    try:
        customers = load_customer_data()
        
        # Basic stats
        total_customers = len(customers)
        active_accounts = len([c for c in customers if c['account_status'] == 'active'])
        frozen_accounts = len([c for c in customers if c['account_status'] == 'frozen'])
        
        # Account type distribution
        account_types = {}
        for customer in customers:
            account_type = customer['account_type']
            account_types[account_type] = account_types.get(account_type, 0) + 1
        
        # Risk level distribution
        risk_levels = {}
        for customer in customers:
            risk_level = customer['risk_level']
            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        # Loan statistics
        customers_with_loans = len([c for c in customers if c['has_loans'] == 'yes'])
        total_loan_amount = sum([float(c['loan_amounts']) for c in customers if c['has_loans'] == 'yes'])
        total_monthly_payments = sum([float(c['monthly_payments']) for c in customers if c['has_loans'] == 'yes'])
        
        # Loan type distribution
        loan_types = {}
        for customer in customers:
            if customer['has_loans'] == 'yes' and customer['loan_types'] != 'none':
                loan_type = customer['loan_types']
                loan_types[loan_type] = loan_types.get(loan_type, 0) + 1
        
        # Credit score statistics
        credit_scores = [c['credit_score'] for c in customers]
        avg_credit_score = sum(credit_scores) / len(credit_scores) if credit_scores else 0
        
        # Balance statistics
        balances = [float(c['balance']) for c in customers]
        total_balance = sum(balances)
        avg_balance = total_balance / len(balances) if balances else 0
        
        return jsonify({
            "total_customers": total_customers,
            "active_accounts": active_accounts,
            "frozen_accounts": frozen_accounts,
            "account_types": account_types,
            "risk_levels": risk_levels,
            "loan_stats": {
                "customers_with_loans": customers_with_loans,
                "total_loan_amount": total_loan_amount,
                "total_monthly_payments": total_monthly_payments,
                "loan_types": loan_types
            },
            "credit_score_stats": {
                "average": round(avg_credit_score, 2),
                "min": min(credit_scores) if credit_scores else 0,
                "max": max(credit_scores) if credit_scores else 0
            },
            "balance_stats": {
                "total_balance": total_balance,
                "average_balance": avg_balance,
                "min_balance": min(balances) if balances else 0,
                "max_balance": max(balances) if balances else 0
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error generating admin stats: {e}")
        return jsonify({"error": "Failed to generate statistics"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "customer_count": len(banking_assistant.customers),
        "ollama_endpoint": OLLAMA_ENDPOINT
    })

@app.route('/api/customer/usernames', methods=['GET'])
def list_customer_usernames():
    """List available customer usernames for login"""
    customers = load_customer_data()
    usernames = [{"username": c['username'], "name": f"{c['first_name']} {c['last_name']}"} for c in customers]
    return jsonify({
        "usernames": usernames,
        "count": len(usernames),
        "note": "Use the password_hash from CSV as the password for login"
    })

@app.route('/api/endpoints', methods=['GET'])
def list_endpoints():
    """List available API endpoints"""
    endpoints = [
        {"method": "GET", "path": "/api/health", "description": "Health check"},
        {"method": "POST", "path": "/api/auth/login", "description": "User login"},
        {"method": "POST", "path": "/api/auth/logout", "description": "User logout"},
        {"method": "GET", "path": "/api/auth/status", "description": "Authentication status"},
        {"method": "GET", "path": "/api/test-connection", "description": "Test Ollama connection"},
        {"method": "POST", "path": "/api/chat", "description": "Send chat message to AI assistant"},
        {"method": "GET", "path": "/api/customer/random", "description": "Get random customer profile"},
        {"method": "GET", "path": "/api/customer/stats", "description": "Get customer statistics"},
        {"method": "GET", "path": "/api/customer/search?q=<query>", "description": "Search customers"},
        {"method": "GET", "path": "/api/customer/loan-type/<type>", "description": "Get customers by loan type"},
        {"method": "GET", "path": "/api/customer/risk-level/<level>", "description": "Get customers by risk level"},
        {"method": "GET", "path": "/api/customer/usernames", "description": "List customer usernames for login"},
        {"method": "POST", "path": "/api/loan/calculate", "description": "Calculate loan payment"},
        {"method": "GET", "path": "/api/endpoints", "description": "List all endpoints"}
    ]
    return jsonify({"endpoints": endpoints})

if __name__ == '__main__':
    print("🏦 Enhanced Banking Assistant Backend")
    print("=" * 50)
    print(f"📊 Loaded {len(banking_assistant.customers)} customers")
    print(f"🤖 Ollama endpoint: {OLLAMA_ENDPOINT}")
    print(f"🧠 Model: {MODEL_NAME}")
    print(f"👥 Available users: {', '.join(USERS.keys())}")
    print("=" * 50)
    print("Starting server on http://localhost:5001")
    print("Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 