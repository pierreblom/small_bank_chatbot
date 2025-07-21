# Banking Chatbot Project

## Project Structure

```
chatbot/
├── BE/                    # Backend
│   ├── config/           # Configuration files
│   ├── models/           # Data models
│   ├── routes/           # API routes
│   ├── utils/            # Utility functions
│   ├── logs/             # Log files
│   ├── app.py            # Main Flask application
│   ├── list_users.py     # User management
│   ├── start.sh          # Startup script
│   └── requirements.txt  # Python dependencies
├── FE/                    # Frontend
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   ├── images/           # Images and assets
│   ├── pages/            # Additional pages
│   ├── index.html        # Main landing page
│   ├── login.html        # Login page
│   ├── admin_dashboard.html
│   ├── loan-calculator.html
│   └── small-bank-chat-backend.html
├── data/                  # Data files
│   ├── backups/          # Data backups
│   ├── exports/          # Data exports
│   ├── schemas/          # Database schemas
│   ├── README.md         # Data documentation
│   ├── banking_customers.csv
│   ├── customer_profiles.csv
│   ├── accounts.csv
│   ├── loans.csv
│   ├── support_issues.csv
│   ├── password_resets.csv
│   └── transactions.csv
└── README.md             # This file
```

## Quick Start

1. **Backend Setup:**
   ```bash
   cd BE
   pip install -r requirements.txt
   python app.py
   ```

2. **Frontend Access:**
   - Open `FE/index.html` in your browser
   - Or serve the FE directory with a web server

3. **Data Management:**
   - All CSV files are in the `data/` directory
   - See `data/README.md` for detailed data documentation

## Features

- **Customer Management:** Complete customer profiles and account management
- **Loan Processing:** Loan calculator and loan portfolio management
- **Admin Dashboard:** Administrative interface for bank operations
- **Data Analytics:** Comprehensive financial data analysis
- **Secure Authentication:** User login and security features

## Data Overview

- **51 customers** with complete financial profiles
- **39 active loans** worth $3.1 million
- **Multiple account types:** Checking, Savings, Credit Cards, Business
- **Comprehensive analytics:** Income, expenses, credit scores, risk levels

## Development

- **Backend:** Python Flask application
- **Frontend:** HTML, CSS, JavaScript
- **Data:** CSV files with normalized structure
- **Documentation:** Markdown files throughout the project
