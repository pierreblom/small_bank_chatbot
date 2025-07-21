# Banking Data Organization

This directory contains organized banking data split into separate CSV files for better data management:

## Files Description:

### 1. customer_profiles.csv
- Basic customer information (name, contact details, security info)
- Primary key: customer_id

### 2. accounts.csv  
- Account details (type, status, balance, credit score)
- Foreign key: customer_id

### 3. loans.csv
- Loan information (type, amount, monthly payments)
- Foreign key: customer_id

### 4. support_issues.csv
- Customer support history and common issues
- Foreign key: customer_id

### 5. password_resets.csv
- Password reset token information
- Foreign key: customer_id

### 6. transactions.csv
- Transaction history (simplified)
- Foreign key: customer_id

## Data Relationships:
- All files are linked by customer_id
- One customer can have multiple loans and transactions
- Each customer has one profile and one primary account

## Usage:
- Use customer_id to join data across files
- Original banking_customers.csv remains as backup
