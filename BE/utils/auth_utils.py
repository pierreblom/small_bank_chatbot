import hashlib
import uuid
import csv
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from functools import wraps
from flask import session, request, jsonify, redirect, make_response

logger = logging.getLogger(__name__)

def create_multi_session_cookie(user_data: Dict, response: jsonify) -> jsonify:
    """Create session cookie with role-specific name for concurrent sessions"""
    role = user_data.get('role', 'customer')
    username = user_data.get('username', '')
    
    # Create role-specific session cookie name
    session_cookie_name = f"session_{role}_{username}"
    
    # Create session data
    session_data = {
        'user_id': username,
        'user_role': role,
        'user_name': user_data.get('name', ''),
        'customer_data': user_data.get('customer_data', {}),
        '_created': datetime.now().timestamp()
    }
    
    # Set the role-specific session cookie
    response.set_cookie(
        session_cookie_name,
        str(session_data),  # In production, use proper session serialization
        max_age=86400,  # 24 hours
        path='/',
        domain=None,
        secure=False,
        httponly=True,
        samesite='Lax'
    )
    
    # Also set a general session cookie for backward compatibility
    response.set_cookie(
        'session',
        str(session_data),
        max_age=86400,
        path='/',
        domain=None,
        secure=False,
        httponly=True,
        samesite='Lax'
    )
    
    return response

def get_current_session_data(request) -> Optional[Dict]:
    """Get current session data from role-specific cookies"""
    cookies = request.cookies
    
    # Check for role-specific session cookies first
    for cookie_name, cookie_value in cookies.items():
        if cookie_name.startswith('session_'):
            try:
                # In production, use proper session deserialization
                session_data = eval(cookie_value)  # Simple for demo - use proper serialization in production
                if isinstance(session_data, dict) and 'user_id' in session_data:
                    return session_data
            except:
                continue
    
    # Fallback to regular session
    if 'user_id' in session:
        return {
            'user_id': session.get('user_id'),
            'user_role': session.get('user_role'),
            'user_name': session.get('user_name'),
            'customer_data': session.get('customer_data', {}),
            '_created': session.get('_created')
        }
    
    return None

def clear_session_cookies(response: jsonify, username: str = None, role: str = None) -> jsonify:
    """Clear all session cookies for a user"""
    cookies = request.cookies if request else {}
    
    # Clear role-specific cookies
    for cookie_name in cookies.keys():
        if cookie_name.startswith('session_'):
            if username and role:
                # Clear specific user's session
                if cookie_name == f"session_{role}_{username}":
                    response.delete_cookie(cookie_name, path='/', domain=None)
            else:
                # Clear all session cookies
                response.delete_cookie(cookie_name, path='/', domain=None)
    
    # Clear general session cookie
    response.delete_cookie('session', path='/', domain=None)
    
    return response

def validate_customer_login(csv_file_path: str, username: str, password: str) -> Optional[Dict]:
    """Validate customer login using CSV data"""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for customer in reader:
                if customer['username'] == username:
                    # Hash the input password and compare with stored hash
                    hashed_input = hashlib.sha256(password.encode()).hexdigest()
                    
                    # Check if password matches (either hashed or plain text for demo)
                    # In production, you'd use proper password hashing like bcrypt
                    if customer['password_hash'] == hashed_input or customer['password_hash'] == password:
                        # Determine role based on account_type
                        role = "admin" if customer['account_type'] == 'admin' else "customer"
                        
                        # Log successful login for security monitoring
                        logger.info(f"Successful login for user: {username} (role: {role})")
                        
                        return {
                            "username": customer['username'],
                            "role": role,
                            "name": f"{customer['first_name']} {customer['last_name']}",
                            "customer_data": customer
                        }
                    else:
                        # Log failed login attempt for security monitoring
                        logger.warning(f"Failed login attempt for user: {username}")
                        break
    except Exception as e:
        logger.error(f"Error validating login: {e}")
    
    return None

def update_customer_password(csv_file_path: str, username: str, new_password: str) -> bool:
    """Update customer password in CSV"""
    try:
        # Read all customers
        customers = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
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
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
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

def generate_reset_token(csv_file_path: str, username: str) -> Optional[str]:
    """Generate a password reset token for a user"""
    try:
        # Read all customers
        customers = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
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
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
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

def validate_reset_token(csv_file_path: str, username: str, token: str) -> bool:
    """Validate a password reset token"""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for customer in reader:
                if customer['username'] == username:
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
    except Exception as e:
        logger.error(f"Error validating reset token: {e}")
    
    return False

def login_required(f):
    """Decorator to require login for protected API routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session data in cookies first
        session_data = get_current_session_data(request)
        
        if not session_data or 'user_id' not in session_data:
            logger.warning(f"Unauthorized API access attempt from {request.remote_addr}")
            return jsonify({"error": "Authentication required"}), 401
        
        # Check if session has expired (24 hours)
        session_created = session_data.get('_created', datetime.now().timestamp())
        if datetime.now().timestamp() - session_created > 86400:  # 24 hours
            logger.warning(f"Session expired for user {session_data['user_id']}")
            return jsonify({"error": "Session expired"}), 401
        
        # Store session data in Flask session for backward compatibility
        session.update(session_data)
            
        return f(*args, **kwargs)
    return decorated_function

def login_required_page(f):
    """Decorator to require login for protected page routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session data in cookies first
        session_data = get_current_session_data(request)
        
        if not session_data or 'user_id' not in session_data:
            logger.warning(f"Unauthorized page access attempt from {request.remote_addr}")
            return redirect('/login.html')
        
        # Check if session has expired (24 hours)
        session_created = session_data.get('_created', datetime.now().timestamp())
        if datetime.now().timestamp() - session_created > 86400:  # 24 hours
            logger.warning(f"Session expired for user {session_data['user_id']}")
            return redirect('/login.html')
        
        # Store session data in Flask session for backward compatibility
        session.update(session_data)
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session data in cookies first
        session_data = get_current_session_data(request)
        
        if not session_data or 'user_id' not in session_data:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session_data.get('user_role')
        if user_role != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        
        # Store session data in Flask session for backward compatibility
        session.update(session_data)
        
        return f(*args, **kwargs)
    return decorated_function 