# DBeaver Import Guide for Banking Data

This guide will help you import your banking data into DBeaver. You have several options depending on your database system.

## Option 1: Using SQL Scripts (Recommended)

### Step 1: Create Database Schema

First, create the database tables with proper relationships:

```sql
-- Create customer_profiles table
CREATE TABLE customer_profiles (
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
CREATE TABLE accounts (
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
CREATE TABLE loans (
    loan_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(10),
    loan_type VARCHAR(50),
    loan_amount DECIMAL(15,2),
    monthly_payment DECIMAL(15,2),
    loan_status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);

-- Create support_issues table
CREATE TABLE support_issues (
    issue_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(10),
    common_issues TEXT,
    last_contact_date DATE,
    issue_status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);

-- Create password_resets table
CREATE TABLE password_resets (
    reset_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(10),
    reset_token VARCHAR(255),
    expiry_date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);

-- Create transactions table
CREATE TABLE transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(10),
    transaction_date DATE,
    transaction_type VARCHAR(50),
    amount DECIMAL(15,2),
    description TEXT,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(customer_id)
);
```

### Step 2: Import Data Using DBeaver's Import Feature

1. **Open DBeaver** and connect to your database
2. **Right-click on your database** → Select "Import Data"
3. **Choose "CSV"** as the import format
4. **Select the CSV file** you want to import
5. **Configure the import settings:**
   - Check "First row is header"
   - Set delimiter to comma (,)
   - Set quote character to double quote (")
6. **Map columns** to your table structure
7. **Review and execute** the import

### Step 3: Import Each Table

Import the tables in this order to maintain referential integrity:

1. `customer_profiles.csv` → `customer_profiles` table
2. `accounts.csv` → `accounts` table  
3. `loans.csv` → `loans` table
4. `support_issues.csv` → `support_issues` table
5. `password_resets.csv` → `password_resets` table
6. `transactions.csv` → `transactions` table

## Option 2: Using SQL INSERT Statements

If you prefer to use SQL INSERT statements, you can generate them from your CSV files:

### For customer_profiles table:
```sql
INSERT INTO customer_profiles (customer_id, first_name, last_name, email, phone, username, password_hash, security_question, security_answer, preferred_contact_method, risk_level, account_opened_date) VALUES
('CUST001', 'John', 'Smith', 'john.smith@email.com', '555-0101', 'johnsmith', 'p', 'What was your first pet''s name?', 'Fluffy', 'email', 'low', '2020-03-12'),
('CUST002', 'Sarah', 'Johnson', 'sarah.j@email.com', '555-0102', 'sarahjohnson', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/5QqHh6e', 'What city were you born in?', 'Chicago', 'phone', 'low', '2018-07-22');
-- Continue for all records...
```

## Option 3: Using Database-Specific Tools

### For PostgreSQL:
```bash
# Using psql COPY command
\copy customer_profiles FROM 'path/to/customer_profiles.csv' WITH (FORMAT csv, HEADER true);
```

### For MySQL:
```sql
-- Using LOAD DATA INFILE
LOAD DATA INFILE 'path/to/customer_profiles.csv' 
INTO TABLE customer_profiles 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;
```

### For SQLite:
```sql
-- Using .import command in SQLite CLI
.mode csv
.import customer_profiles.csv customer_profiles
```

## Troubleshooting Tips

1. **Character Encoding**: If you see garbled text, try UTF-8 encoding
2. **Date Formats**: Ensure your database accepts the date format (YYYY-MM-DD)
3. **Foreign Key Constraints**: Import parent tables before child tables
4. **Data Types**: Verify that numeric fields don't contain text
5. **Duplicate Keys**: Check for duplicate primary keys before importing

## Verification Queries

After importing, run these queries to verify your data:

```sql
-- Check record counts
SELECT 'customer_profiles' as table_name, COUNT(*) as record_count FROM customer_profiles
UNION ALL
SELECT 'accounts', COUNT(*) FROM accounts
UNION ALL
SELECT 'loans', COUNT(*) FROM loans
UNION ALL
SELECT 'support_issues', COUNT(*) FROM support_issues
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions;

-- Check relationships
SELECT 
    cp.customer_id,
    cp.first_name,
    cp.last_name,
    a.balance,
    COUNT(l.loan_id) as loan_count,
    COUNT(t.transaction_id) as transaction_count
FROM customer_profiles cp
LEFT JOIN accounts a ON cp.customer_id = a.customer_id
LEFT JOIN loans l ON cp.customer_id = l.customer_id
LEFT JOIN transactions t ON cp.customer_id = t.customer_id
GROUP BY cp.customer_id, cp.first_name, cp.last_name, a.balance
LIMIT 10;
```

## Database System Recommendations

- **PostgreSQL**: Best for complex queries and data integrity
- **MySQL**: Good for web applications and moderate workloads  
- **SQLite**: Perfect for development and testing
- **SQL Server**: Good for enterprise environments

Choose the database system that best fits your needs and follow the appropriate import method above. 