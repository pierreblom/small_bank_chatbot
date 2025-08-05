from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

utility_bp = Blueprint('utility', __name__)

def init_utility_routes(app, banking_assistant):
    """Initialize utility routes"""
    
    @utility_bp.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "customer_count": len(banking_assistant.customers),
            "session_info": {
                "has_session": 'user_id' in session,
                "user_id": session.get('user_id'),
                "user_role": session.get('user_role')
            }
        })

    @utility_bp.route('/api/endpoints', methods=['GET'])
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

    # Register the blueprint
    app.register_blueprint(utility_bp) 