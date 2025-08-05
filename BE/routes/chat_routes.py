from flask import Blueprint, request, jsonify, session
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth_utils import login_required
from utils.chat_utils import send_chat_message, test_ollama_connection

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

def init_chat_routes(app, ollama_endpoint, model_name):
    """Initialize chat routes"""
    
    @chat_bp.route('/api/chat', methods=['POST'])
    @login_required
    def chat():
        """Handle chat messages with Ollama"""
        try:
            data = request.get_json()
            message = data.get('message', '').strip()
            conversation_history = data.get('history', [])
            
            if not message:
                return jsonify({"error": "Message is required"}), 400
            
            # Get customer-specific data if available
            customer_data = session.get('customer_data')
            
            # Send message to Ollama
            result = send_chat_message(
                ollama_endpoint=ollama_endpoint,
                model_name=model_name,
                message=message,
                conversation_history=conversation_history,
                customer_data=customer_data
            )
            
            if "error" in result:
                return jsonify(result), 500
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @chat_bp.route('/api/test-connection', methods=['GET'])
    @login_required
    def test_connection():
        """Test Ollama connection"""
        result = test_ollama_connection(ollama_endpoint, model_name)
        
        if result.get("status") == "success":
            return jsonify(result)
        else:
            return jsonify(result), 503

    # Register the blueprint
    app.register_blueprint(chat_bp) 