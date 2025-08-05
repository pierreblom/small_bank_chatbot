from flask import Flask
from flask_cors import CORS
import logging
import os
from datetime import timedelta

# Import our modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.app_config import AppConfig
from models.banking_assistant import BankingAssistant
from routes.auth_routes import init_auth_routes
from routes.chat_routes import init_chat_routes
from routes.customer_routes import init_customer_routes
from routes.admin_routes import init_admin_routes
from routes.page_routes import init_page_routes
from routes.utility_routes import init_utility_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = AppConfig()
    
    # Configure Flask app
    app.secret_key = config.get_secret_key()
    
    # Configure session
    session_config = config.get_session_config()
    for key, value in session_config.items():
        app.config[key] = value
    
    # Configure CORS
    cors_config = config.get_cors_config()
    CORS(app, 
         supports_credentials=cors_config['supports_credentials'],
         origins=cors_config['origins'],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Set up file paths
    csv_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "banking_customers.csv")
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "FE")
    
    # Debug: Print the CSV file path to help with troubleshooting
    print(f"CSV file path: {csv_file_path}")
    print(f"CSV file exists: {os.path.exists(csv_file_path)}")
    print(f"Frontend path: {frontend_path}")
    print(f"Frontend exists: {os.path.exists(frontend_path)}")
    
    # Initialize banking assistant
    banking_assistant = BankingAssistant(csv_file_path)
    
    # Initialize routes
    init_auth_routes(app, csv_file_path)
    init_chat_routes(app, config.get_ollama_endpoint(), config.get_ollama_model())
    init_customer_routes(app, banking_assistant)
    init_admin_routes(app, csv_file_path)
    init_page_routes(app, frontend_path)
    init_utility_routes(app, banking_assistant)
    
    return app, banking_assistant, config

def main():
    """Main application entry point"""
    app, banking_assistant, config = create_app()
    
    print("🏦 Enhanced Banking Assistant Backend (Modular)")
    print("=" * 50)
    print(f"📊 Loaded {len(banking_assistant.customers)} customers")
    print(f"🤖 Ollama endpoint: {config.get_ollama_endpoint()}")
    print(f"🧠 Model: {config.get_ollama_model()}")
    
    # Get some sample users for display
    customers = banking_assistant.customers
    admin_users = [c['username'] for c in customers if c['account_type'] == 'admin']
    customer_users = [c['username'] for c in customers if c['account_type'] != 'admin']
    
    print(f"👥 Available admin users: {', '.join(admin_users[:3])}{'...' if len(admin_users) > 3 else ''}")
    print(f"👤 Available customer users: {', '.join(customer_users[:5])}{'...' if len(customer_users) > 5 else ''}")
    print("=" * 50)
    print(f"Starting server on http://{config.get_app_host()}:{config.get_app_port()}")
    print("Press Ctrl+C to stop")
    
    app.run(
        debug=config.get_app_debug(), 
        host=config.get_app_host(), 
        port=config.get_app_port(), 
        use_reloader=False
    )

if __name__ == '__main__':
    main() 