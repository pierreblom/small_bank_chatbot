from flask import Blueprint, request, jsonify, session, redirect, send_file
import logging
import os
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth_utils import login_required_page

logger = logging.getLogger(__name__)

page_bp = Blueprint('pages', __name__)

def init_page_routes(app, frontend_path):
    """Initialize page routes"""
    
    @page_bp.route('/')
    def index():
        """Serve the main index page"""
        # Check if user is already authenticated
        if 'user_id' in session:
            user_role = session.get('user_role')
            if user_role == 'admin':
                return redirect('/admin')
            else:
                return redirect('/chat')
        
        # If not authenticated, redirect to login
        return redirect('/login.html')

    @page_bp.route('/test-auth.html')
    def test_auth_page():
        """Serve the authentication test page"""
        try:
            test_file_path = os.path.join(frontend_path, "test-auth.html")
            return send_file(test_file_path, mimetype='text/html')
        except FileNotFoundError:
            return "Test page not found", 404

    @page_bp.route('/test_session.html')
    def test_session_page():
        """Serve the session test page"""
        try:
            test_file_path = os.path.join(os.path.dirname(frontend_path), "test_session.html")
            return send_file(test_file_path, mimetype='text/html')
        except FileNotFoundError:
            return "Test session page not found", 404

    @page_bp.route('/test_fixes.html')
    def test_fixes_page():
        """Serve the fixes test page"""
        try:
            test_file_path = os.path.join(os.path.dirname(frontend_path), "test_fixes.html")
            return send_file(test_file_path, mimetype='text/html')
        except FileNotFoundError:
            return "Test fixes page not found", 404

    @page_bp.route('/test_logout_simple.html')
    def test_logout_simple_page():
        """Serve the logout test page"""
        try:
            test_file_path = os.path.join(os.path.dirname(frontend_path), "test_logout_simple.html")
            return send_file(test_file_path, mimetype='text/html')
        except FileNotFoundError:
            return "Test logout page not found", 404

    @page_bp.route('/login.html')
    def login_page():
        """Serve the login page"""
        # Check if user is already authenticated
        if 'user_id' in session:
            user_role = session.get('user_role')
            if user_role == 'admin':
                return redirect('/admin')
            else:
                return redirect('/chat')
        
        try:
            login_file_path = os.path.join(frontend_path, "login.html")
            logger.info(f"Login page path: {login_file_path}")
            logger.info(f"File exists: {os.path.exists(login_file_path)}")
            
            response = send_file(login_file_path, mimetype='text/html')
            
            # Add cache-busting headers to prevent caching
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        except FileNotFoundError:
            logger.error(f"Login page not found at: {login_file_path}")
            return "Login page not found", 404

    @page_bp.route('/images/<filename>')
    def serve_image(filename):
        """Serve images from the FE/images directory"""
        try:
            image_file_path = os.path.join(frontend_path, "images", filename)
            return send_file(image_file_path)
        except FileNotFoundError:
            return "Image not found", 404

    @page_bp.route('/css/<filename>')
    def serve_css(filename):
        """Serve CSS files from the FE/css directory"""
        try:
            css_file_path = os.path.join(frontend_path, "css", filename)
            return send_file(css_file_path, mimetype='text/css')
        except FileNotFoundError:
            return "CSS file not found", 404

    @page_bp.route('/js/<filename>')
    def serve_js(filename):
        """Serve JavaScript files from the FE/js directory"""
        try:
            js_file_path = os.path.join(frontend_path, "js", filename)
            return send_file(js_file_path, mimetype='application/javascript')
        except FileNotFoundError:
            return "JavaScript file not found", 404

    @page_bp.route('/Gemini_Generated_Image_b2kiqjb2kiqjb2ki.png')
    def serve_bank_logo():
        """Serve the bank logo image"""
        try:
            logo_file_path = os.path.join(frontend_path, "images", "Gemini_Generated_Image_b2kiqjb2kiqjb2ki.png")
            return send_file(logo_file_path, mimetype='image/png')
        except FileNotFoundError:
            return "Logo not found", 404

    @page_bp.route('/loan-calculator.html')
    @login_required_page
    def loan_calculator():
        """Serve the loan calculator page"""
        try:
            loan_file_path = os.path.join(frontend_path, "loan-calculator.html")
            return send_file(loan_file_path, mimetype='text/html')
        except FileNotFoundError:
            return "Loan calculator not found", 404

    @page_bp.route('/chat')
    @login_required_page
    def chat_page():
        """Serve the chat page (requires authentication)"""
        try:
            chat_file_path = os.path.join(frontend_path, "small-bank-chat-backend.html")
            response = send_file(chat_file_path, mimetype='text/html')
            
            # Add cache-busting headers with unique timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = f'Mon, 04 Aug 2025 12:02:{timestamp} GMT'
            response.headers['ETag'] = f'v1.0.4-{timestamp}'
            
            return response
        except FileNotFoundError:
            return "Chat page not found", 404

    @page_bp.route('/admin')
    @login_required_page
    def admin_page():
        """Serve the admin dashboard page (requires admin authentication)"""
        # Check if user is admin (session check already done by decorator)
        user_role = session.get('user_role')
        
        # Check if user is admin
        if user_role != 'admin':
            return redirect('/chat')
        
        try:
            admin_file_path = os.path.join(frontend_path, "admin_dashboard.html")
            return send_file(admin_file_path, mimetype='text/html')
        except FileNotFoundError:
            return "Admin dashboard not found", 404

    @page_bp.route('/admin_dashboard.html')
    @login_required_page
    def admin_dashboard_page():
        """Serve the admin dashboard page"""
        try:
            admin_file_path = os.path.join(frontend_path, "admin_dashboard.html")
            return send_file(admin_file_path, mimetype='text/html')
        except FileNotFoundError:
            return "Admin dashboard not found", 404

    @page_bp.route('/customer_profile.html')
    def customer_profile_page():
        """Serve the customer profile page"""
        try:
            profile_file_path = os.path.join(frontend_path, "customer_profile.html")
            logger.info(f"Customer profile path: {profile_file_path}")
            logger.info(f"File exists: {os.path.exists(profile_file_path)}")
            
            response = send_file(profile_file_path, mimetype='text/html')
            
            # Add cache-busting headers
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        except FileNotFoundError:
            logger.error(f"Customer profile not found at: {profile_file_path}")
            return "Customer profile not found", 404

    @page_bp.route('/test_customer_profile.html')
    @login_required_page
    def test_customer_profile_page():
        """Serve the customer profile test page"""
        # Check if user is admin
        if session.get('user_role') != 'admin':
            return redirect('/login.html')
        
        try:
            test_file_path = os.path.join(frontend_path, "test_customer_profile.html")
            logger.info(f"Test customer profile path: {test_file_path}")
            logger.info(f"File exists: {os.path.exists(test_file_path)}")
            
            response = send_file(test_file_path, mimetype='text/html')
            
            # Add cache-busting headers
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        except FileNotFoundError:
            logger.error(f"Test customer profile not found at: {test_file_path}")
            return "Test customer profile not found", 404

    # Register the blueprint
    app.register_blueprint(page_bp) 