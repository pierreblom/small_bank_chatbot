from flask import Blueprint, request, jsonify, session
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth_utils import login_required
from models.banking_assistant import BankingAssistant

logger = logging.getLogger(__name__)

customer_bp = Blueprint('customer', __name__)

def init_customer_routes(app, banking_assistant):
    """Initialize customer routes"""
    
    @customer_bp.route('/api/customer/current', methods=['GET'])
    @login_required
    def get_current_customer():
        """Get the current logged-in customer's profile"""
        if 'customer_data' in session:
            return jsonify(session['customer_data'])
        else:
            # Fallback for non-customer users (admin, banker, demo)
            customer = banking_assistant.get_random_customer()
            return jsonify(customer)

    @customer_bp.route('/api/customer/random', methods=['GET'])
    @login_required
    def get_random_customer():
        """Get a random customer profile"""
        customer = banking_assistant.get_random_customer()
        return jsonify(customer)

    @customer_bp.route('/api/customer/search', methods=['GET'])
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

    @customer_bp.route('/api/customer/stats', methods=['GET'])
    @login_required
    def get_customer_stats():
        """Get customer statistics"""
        stats = banking_assistant.get_customer_stats()
        return jsonify(stats)

    @customer_bp.route('/api/customer/loan-type/<loan_type>', methods=['GET'])
    @login_required
    def get_customers_by_loan_type(loan_type):
        """Get customers by loan type"""
        customers = banking_assistant.get_customers_by_loan_type(loan_type)
        return jsonify({
            "loan_type": loan_type,
            "customers": customers,
            "count": len(customers)
        })

    @customer_bp.route('/api/customer/risk-level/<risk_level>', methods=['GET'])
    @login_required
    def get_customers_by_risk_level(risk_level):
        """Get customers by risk level"""
        customers = banking_assistant.get_customers_by_risk_level(risk_level)
        return jsonify({
            "risk_level": risk_level,
            "customers": customers,
            "count": len(customers)
        })

    @customer_bp.route('/api/loan/calculate', methods=['POST'])
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

    @customer_bp.route('/api/customer/my-loan', methods=['GET'])
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

    @customer_bp.route('/api/customer/my-account', methods=['GET'])
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

    # Register the blueprint
    app.register_blueprint(customer_bp) 