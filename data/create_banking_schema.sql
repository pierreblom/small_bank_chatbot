-- Banking Database Schema Creation Script
-- Run this script in DBeaver to create the database structure

-- Create customer_profiles table
CREATE TABLE IF NOT EXISTS customer_profiles (
    customer_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    security_question VARCHAR(200),
    security_answer VARCHAR(100),
    preferred_contact_method VARCHAR(20),
    risk_level VARCHAR(20),
    account_opened_date DATE
);

-- Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
    customer_id VARCHAR(10) PRIMARY KEY,
    account_type VARCHAR(50),
    account_status VARCHAR(20),
    balance DECIMAL(15,2),
    credit_score INTEGER,
    interest_rate DECIMAL(5,2),
    last_transaction_date DATE,
    monthly_income DECIMAL(15,2),
    monthly_expenses DECIMAL(15,2),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);

-- Create loans table
CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(10),
    loan_type VARCHAR(50),
    loan_amount DECIMAL(15,2),
    monthly_payment DECIMAL(15,2),
    loan_status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);

-- Create support_issues table
CREATE TABLE IF NOT EXISTS support_issues (
    issue_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(10),
    common_issues TEXT,
    last_contact_date DATE,
    issue_status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);

-- Create password_resets table
CREATE TABLE IF NOT EXISTS password_resets (
    reset_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(10),
    reset_token VARCHAR(255),
    expiry_date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(10),
    transaction_date DATE,
    transaction_type VARCHAR(50),
    amount DECIMAL(15,2),
    description TEXT,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);

-- Create indexes for better performance
CREATE INDEX idx_customer_profiles_email ON customer_profiles(email);
CREATE INDEX idx_customer_profiles_username ON customer_profiles(username);
CREATE INDEX idx_accounts_balance ON accounts(balance);
CREATE INDEX idx_loans_customer_id ON loans(customer_id);
CREATE INDEX idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);

-- Display table creation confirmation
SELECT 'Database schema created successfully!' as status; 