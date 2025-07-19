# 🏦 Enhanced Banking Assistant with Python Backend

A sophisticated banking chatbot with a Python Flask backend that integrates with Ollama for AI-powered responses and provides comprehensive customer data management capabilities.

## 🚀 Features

### 🤖 AI-Powered Chat
- **Ollama Integration**: Uses local LLM (llama3) for intelligent responses
- **Context Awareness**: Maintains conversation history for coherent interactions
- **Empathetic Responses**: Warm, caring tone with banking expertise
- **Safety First**: Never requests real personal information

### 📊 Customer Data Management
- **50 Fictional Customers**: Comprehensive demo dataset with realistic banking profiles
- **Advanced Search**: Search by name, email, loan type, account type, etc.
- **Statistical Analysis**: Detailed customer demographics and loan distributions
- **Risk Assessment**: Customer risk level categorization

### 💰 Banking Tools
- **Loan Calculator**: Accurate payment calculations with amortization
- **Customer Profiles**: Detailed fictional customer information
- **Account Types**: Checking, savings, credit cards, business accounts
- **Loan Types**: Auto, personal, mortgage, business, student loans

### 🛡️ Security & Privacy
- **Fictional Data Only**: All customer information is demo data
- **No Real Transactions**: Cannot access real accounts or perform transactions
- **Privacy Warnings**: Clear disclaimers throughout the interface
- **Secure Backend**: Proper error handling and input validation

## 📋 Prerequisites

Before running this application, you need:

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running locally
3. **llama3 model** downloaded in Ollama

### Installing Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [https://ollama.ai/download](https://ollama.ai/download)

### Downloading the Model

After installing Ollama, download the llama3 model:
```bash
ollama pull llama3
```

## 🛠️ Installation & Setup

### Method 1: Quick Start (Recommended)

1. **Clone or download the project files**
   ```bash
   # If you have the files locally, navigate to the project directory
   cd chatbot
   ```

2. **Make the start script executable and run it**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   This script will:
   - Create a virtual environment
   - Install dependencies
   - Check Ollama status
   - Start the Flask backend

### Method 2: Manual Setup

1. **Navigate to the project directory**
   ```bash
   cd chatbot
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify file structure**
   ```
   chatbot/
   ├── app.py                          # Flask backend
   ├── requirements.txt                 # Python dependencies
   ├── start.sh                        # Easy startup script
   ├── login.html                      # Authentication page
   ├── admin_dashboard.html            # Admin interface
   ├── small-bank-chat-backend.html    # Main chat interface
   ├── banking_customers.csv           # Customer data
   └── list_users.py                   # User management utility
   ```

## 🚀 How to Run the Application

### Step 1: Start Ollama

**In a new terminal window:**
```bash
ollama serve
```

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**If you haven't downloaded the model yet:**
```bash
ollama pull llama3
```

### Step 2: Start the Flask Backend

**Option A: Using the start script (Recommended)**
```bash
./start.sh
```

**Option B: Manual start**
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the Flask application
python app.py
```

You should see output like:
```
🏦 Enhanced Banking Assistant - Starting Up
==========================================
📦 Creating virtual environment...
🔧 Activating virtual environment...
📥 Installing dependencies...
🤖 Checking Ollama status...
🚀 Starting Flask backend on http://localhost:5001
```

### Step 3: Access the Application

1. **Open your web browser**
2. **Navigate to**: `http://localhost:5001`
3. **You'll be redirected to the login page**

### Step 4: Login

Use one of these demo credentials:

- **Admin User**: `admin` / `admin123` (Full access to all features)
- **Banker User**: `banker` / `banker123` (Bank representative access)
- **Demo User**: `demo` / `demo123` (Standard user access)

## 🎯 Using the Application

### Main Features

1. **Chat Interface**: Send messages and get AI-powered responses
2. **Test Backend**: Verify Ollama connection is working
3. **Demo Customer**: View a random customer profile
4. **Show Stats**: See comprehensive customer statistics
5. **Search Customers**: Find specific customers by name or criteria
6. **Loan Calculator**: Calculate loan payments with different parameters
7. **Admin Dashboard**: Access advanced features (admin users only)

### Navigation

- **Chat Page**: Main conversation interface
- **Admin Dashboard**: Advanced customer management (admin only)
- **Logout**: End your session and return to login

## 🔧 Configuration

### Backend Configuration

Edit `app.py` to modify settings:

```python
# Configuration
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"
CSV_FILE = "banking_customers.csv"
```

### Port Configuration

The application runs on port 5001 by default. To change this, modify the last line in `app.py`:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. "Backend Offline" Status
**Problem**: The frontend can't connect to the Flask backend
**Solution**:
```bash
# Check if Flask is running
curl http://localhost:5001/api/health

# If not running, start it:
python app.py
```

#### 2. "Ollama Connection Failed"
**Problem**: The backend can't connect to Ollama
**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve

# Check if llama3 model is installed
ollama list

# If missing, download it:
ollama pull llama3
```

#### 3. "CSV File Not Found"
**Problem**: Customer data can't be loaded
**Solution**:
```bash
# Ensure you're in the correct directory
ls -la banking_customers.csv

# If missing, check the file exists in the project
```

#### 4. Port Already in Use
**Problem**: Port 5001 is already occupied
**Solution**:
```bash
# Find what's using the port
lsof -i :5001

# Kill the process or change the port in app.py
```

#### 5. Virtual Environment Issues
**Problem**: Python dependencies not found
**Solution**:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 6. Permission Denied on start.sh
**Problem**: Can't execute the start script
**Solution**:
```bash
chmod +x start.sh
./start.sh
```

### Debug Mode

Run the backend in debug mode for detailed error messages:
```bash
python app.py
```

Check the terminal output for any error messages or connection issues.

### Logs and Monitoring

The application provides detailed logging. Check the terminal output for:
- Connection status
- API requests
- Error messages
- Ollama responses

## 🔒 Security Considerations

- **Demo Only**: This application is for demonstration purposes
- **Fictional Data**: All customer information is completely fictional
- **No Real Banking**: Cannot perform actual banking transactions
- **Local Deployment**: Designed for local development and testing
- **Input Validation**: Backend validates all inputs to prevent injection attacks

## 📊 Customer Data Structure

The CSV file contains 50 fictional customers with the following fields:

- `customer_id` - Unique customer identifier
- `first_name`, `last_name` - Customer name
- `email`, `phone` - Contact information
- `account_type` - Checking, savings, credit card, business
- `account_status` - Active, frozen, etc.
- `balance` - Account balance
- `credit_score` - Credit score (580-810)
- `last_transaction_date` - Most recent transaction
- `preferred_contact_method` - Email, phone, text
- `common_issues` - Typical customer problems
- `risk_level` - Low, medium, high
- `account_opened_date` - Account creation date
- `has_loans` - Yes/no
- `loan_types` - Auto, personal, mortgage, business, student, none
- `loan_amounts` - Total loan amount
- `monthly_payments` - Monthly loan payment

## 🎨 Customization

### Adding New Features

1. **New API Endpoints**: Add routes to `app.py`
2. **Frontend Features**: Modify the HTML/JavaScript
3. **Customer Data**: Update `banking_customers.csv`
4. **AI Prompts**: Modify the `SYSTEM_PROMPT` in `app.py`

### Styling

The interface uses modern CSS with:
- Gradient backgrounds
- Responsive design
- Smooth animations
- Professional banking color scheme

## 📝 License

This project is for educational and demonstration purposes. All customer data is fictional.

## 🤝 Contributing

Feel free to enhance this project by:
- Adding new banking features
- Improving the UI/UX
- Expanding the customer dataset
- Adding more AI capabilities
- Implementing additional security measures

---

**Note**: This is a demonstration system. All customer data is fictional and for testing purposes only. Do not use for real banking operations.