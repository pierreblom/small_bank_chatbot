from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth_utils import (
    validate_customer_login, 
    update_customer_password, 
    generate_reset_token, 
    validate_reset_token
)

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def init_auth_routes(app, csv_file_path):
    """Initialize authentication routes"""
    
    @auth_bp.route('/api/auth/login', methods=['POST'])
    def login():
        """Handle user login"""
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            logger.info(f"Login attempt for username: {username}")
            logger.info(f"Session before login: {dict(session)}")
            
            if not username or not password:
                return jsonify({"error": "Username and password are required"}), 400
            
            # Check customer login from CSV data only
            customer_user = validate_customer_login(csv_file_path, username, password)
            if customer_user:
                session['user_id'] = customer_user['username']
                session['user_role'] = customer_user['role']
                session['user_name'] = customer_user['name']
                session['customer_data'] = customer_user['customer_data']  # Store customer data in session
                session['_created'] = datetime.now().timestamp()  # Add session creation timestamp
                
                # Force session to be saved
                session.modified = True
                
                logger.info(f"Customer {username} logged in successfully")
                logger.info(f"Session after customer login: {dict(session)}")
                logger.info(f"Session modified flag: {session.modified}")
                
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "username": username,
                        "role": customer_user['role'],
                        "name": customer_user['name']
                    }
                })
            
            logger.info(f"Login failed for username: {username}")
            return jsonify({"error": "Invalid username or password"}), 401
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({"error": "Login failed"}), 500

    @auth_bp.route('/api/auth/logout', methods=['POST'])
    def logout():
        """Handle user logout"""
        logger.info(f"Logout request - Session before: {dict(session)}")
        
        # Clear all session data
        session.pop('user_id', None)
        session.pop('user_role', None)
        session.pop('user_name', None)
        session.pop('customer_data', None)
        session.pop('_created', None)
        session.clear()
        
        logger.info(f"Logout completed - Session after: {dict(session)}")
        
        # Create response and properly expire the session cookie
        response = jsonify({"success": True, "message": "Logout successful"})
        
        # Force session to be marked as modified and cleared
        session.modified = True
        
        # Set session cookie to expire immediately and clear it
        response.set_cookie(
            'session', 
            '', 
            expires=0, 
            max_age=0,
            path='/',
            domain=None,
            secure=False,
            httponly=True,
            samesite='Lax'
        )
        
        # Also clear the Flask session cookie
        response.delete_cookie('session', path='/', domain=None)
        
        return response

    @auth_bp.route('/api/auth/force-clear-session', methods=['POST'])
    def force_clear_session():
        """Force clear session for testing purposes"""
        logger.info(f"Force clear session request - Session before: {dict(session)}")
        
        # Clear all session data
        session.clear()
        session.modified = True
        
        logger.info(f"Force clear session completed - Session after: {dict(session)}")
        
        # Create response and properly expire the session cookie
        response = jsonify({"success": True, "message": "Session cleared"})
        
        # Set session cookie to expire immediately and clear it
        response.set_cookie(
            'session', 
            '', 
            expires=0, 
            max_age=0,
            path='/',
            domain=None,
            secure=False,
            httponly=True,
            samesite='Lax'
        )
        
        # Also clear the Flask session cookie
        response.delete_cookie('session', path='/', domain=None)
        
        return response

    @auth_bp.route('/api/auth/status', methods=['GET'])
    def auth_status():
        """Get current authentication status"""
        logger.info(f"Auth status check - Session: {dict(session)}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request cookies: {dict(request.cookies)}")
        
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

    @auth_bp.route('/api/auth/forgot-password', methods=['POST'])
    def forgot_password():
        """Handle forgot password request"""
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            
            if not username:
                return jsonify({"error": "Username is required"}), 400
            
            # Generate reset token
            reset_token = generate_reset_token(csv_file_path, username)
            if not reset_token:
                # Don't reveal if user exists or not for security
                return jsonify({
                    "success": True,
                    "message": "If the username exists, a reset link has been sent."
                })
            
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

    @auth_bp.route('/api/auth/reset-password', methods=['POST'])
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
            if not validate_reset_token(csv_file_path, username, token):
                return jsonify({"error": "Invalid or expired reset token"}), 401
            
            # Update password
            if update_customer_password(csv_file_path, username, new_password):
                return jsonify({
                    "success": True,
                    "message": "Password reset successfully"
                })
            else:
                return jsonify({"error": "Failed to update password"}), 500
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return jsonify({"error": "Password reset failed"}), 500

    @auth_bp.route('/api/auth/get-security-question', methods=['GET'])
    def get_security_question():
        """Get security question for a username"""
        try:
            username = request.args.get('username', '').strip()
            
            if not username:
                return jsonify({"error": "Username is required"}), 400
            
            # Read from CSV to get security question
            import csv
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for customer in reader:
                    if customer['username'] == username:
                        return jsonify({
                            "security_question": customer.get('security_question', '')
                        })
            
            return jsonify({"error": "User not found"}), 404
            
        except Exception as e:
            logger.error(f"Get security question error: {e}")
            return jsonify({"error": "Failed to get security question"}), 500

    @auth_bp.route('/api/auth/verify-security-question', methods=['POST'])
    def verify_security_question():
        """Verify security question answer"""
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            answer = data.get('answer', '').strip()
            
            if not username or not answer:
                return jsonify({"error": "Username and answer are required"}), 400
            
            # Read from CSV to verify security answer
            import csv
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for customer in reader:
                    if customer['username'] == username:
                        # Check security answer (case-insensitive)
                        if customer.get('security_answer', '').lower() == answer.lower():
                            return jsonify({
                                "success": True,
                                "message": "Security question verified",
                                "security_question": customer.get('security_question', '')
                            })
                        else:
                            return jsonify({"error": "Incorrect answer"}), 401
            
            return jsonify({"error": "User not found"}), 404
            
        except Exception as e:
            logger.error(f"Security question verification error: {e}")
            return jsonify({"error": "Verification failed"}), 500

    @auth_bp.route('/api/customer/usernames', methods=['GET'])
    def list_customer_usernames():
        """List available customer usernames for login"""
        try:
            import csv
            customers = []
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for customer in reader:
                    customers.append({
                        "username": customer['username'], 
                        "name": f"{customer['first_name']} {customer['last_name']}"
                    })
            
            return jsonify({
                "usernames": customers,
                "count": len(customers),
                "note": "Use the password_hash from CSV as the password for login"
            })
        except Exception as e:
            logger.error(f"Error listing usernames: {e}")
            return jsonify({"error": "Failed to list usernames"}), 500

    # Register the blueprint
    app.register_blueprint(auth_bp) 