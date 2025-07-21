# Data Schema Documentation

## Database Structure

### customer_profiles.csv
- customer_id (Primary Key)
- first_name, last_name, email, phone
- username, password_hash
- security_question, security_answer
- preferred_contact_method, risk_level
- account_opened_date

### accounts.csv
- customer_id (Foreign Key)
- account_type, account_status, balance
- credit_score, interest_rate
- last_transaction_date
- monthly_income, monthly_expenses

### loans.csv
- customer_id (Foreign Key)
- loan_type, loan_amount
- monthly_payment, loan_status

### support_issues.csv
- customer_id (Foreign Key)
- common_issues, last_contact_date
- issue_status

### transactions.csv
- transaction_id (Primary Key)
- customer_id (Foreign Key)
- transaction_date, transaction_type
- amount, description

## Relationships
- All tables linked by customer_id
- One customer can have multiple loans and transactions
- Each customer has one profile and one primary account
