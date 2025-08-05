import csv
import os
import random
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class BankingAssistant:
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.customers = self._load_customer_data()
        self.conversation_history = []
        
    def _load_customer_data(self) -> List[Dict]:
        """Load customer data from CSV file"""
        customers = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
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
            logger.error(f"CSV file {self.csv_file_path} not found")
            return []
        except Exception as e:
            logger.error(f"Error loading customer data: {e}")
            return []
        
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
    
    def get_customer_by_username(self, username: str) -> Dict:
        """Get customer data by username"""
        for customer in self.customers:
            if customer['username'] == username:
                return customer
        return None 