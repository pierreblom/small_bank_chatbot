from flask import Blueprint, request, jsonify, session
import logging
import csv
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth_utils import admin_required

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

def init_admin_routes(app, csv_file_path):
    """Initialize admin routes"""
    
    @admin_bp.route('/api/admin/customers', methods=['GET'])
    @admin_required
    def get_all_customers():
        """Get all customer data (admin only)"""
        try:
            customers = []
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for customer in reader:
                    customers.append(customer)
            
            return jsonify({
                "customers": customers,
                "count": len(customers),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error loading customer data: {e}")
            return jsonify({"error": "Failed to load customer data"}), 500

    @admin_bp.route('/api/admin/customer/<customer_id>', methods=['GET'])
    @admin_required
    def get_customer_by_id(customer_id):
        """Get specific customer by ID (admin only)"""
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for customer in reader:
                    if customer['customer_id'] == customer_id:
                        return jsonify(customer)
            
            return jsonify({"error": "Customer not found"}), 404
        except Exception as e:
            logger.error(f"Error loading customer data: {e}")
            return jsonify({"error": "Failed to load customer data"}), 500

    @admin_bp.route('/api/admin/stats', methods=['GET'])
    @admin_required
    def get_admin_stats():
        """Get comprehensive admin statistics"""
        try:
            customers = []
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for customer in reader:
                    customers.append(customer)
            
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
            credit_scores = [int(c['credit_score']) for c in customers]
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

    # Register the blueprint
    app.register_blueprint(admin_bp) 