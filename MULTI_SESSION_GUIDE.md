# Multi-Session Banking System Guide

## Overview

The Small Bank system now supports **concurrent sessions**, allowing you to login as both an admin and customer simultaneously in different browser tabs. This is perfect for testing and demonstration purposes.

## How It Works

The system uses role-specific session cookies to maintain separate authentication states for different user types:

- **Admin sessions**: Use `session_admin_username` cookies
- **Customer sessions**: Use `session_customer_username` cookies
- **Backward compatibility**: Still supports the original `session` cookie

## Getting Started

### 1. Start the Backend Server

```bash
cd BE
python app_new.py
```

The server will start on `http://localhost:5001`

### 2. Access the Welcome Page

Open your browser and go to:
```
http://localhost:5001
```

You'll see a welcome page with two options:
- **Customer Login** - For regular banking customers
- **Admin Login** - For administrative access

### 3. Login as Admin

1. Click **"Admin Login"** or go directly to `http://localhost:5001/admin_login.html`
2. Use admin credentials:
   - Username: `admin1`
   - Password: `admin123`
3. You'll be redirected to the admin dashboard

### 4. Login as Customer (in a new tab)

1. Open a **new browser tab**
2. Go to `http://localhost:5001`
3. Click **"Customer Login"** or go to `http://localhost:5001/login.html`
4. Use customer credentials:
   - Username: `john_doe`
   - Password: `password123`
5. You'll be redirected to the customer chat interface

### 5. Verify Both Sessions

Both tabs should now show different authenticated sessions:
- **Admin tab**: Shows admin dashboard with statistics
- **Customer tab**: Shows customer chat interface

## Available Credentials

### Admin Users
- `admin1` / `admin123`
- `admin2` / `admin456`

### Customer Users
- `john_doe` / `password123`
- `jane_smith` / `password456`
- `bob_wilson` / `password789`

## Testing the Multi-Session Feature

### Automated Test

Run the test script to verify everything works:

```bash
python test_multi_session.py
```

This will test:
- Admin login
- Customer login
- Concurrent session access
- Admin-only endpoint access
- Proper logout functionality

### Manual Testing

1. **Login as Admin**:
   - Go to `http://localhost:5001/admin_login.html`
   - Login with admin credentials
   - Verify you can access admin dashboard

2. **Login as Customer** (in new tab):
   - Go to `http://localhost:5001/login.html`
   - Login with customer credentials
   - Verify you can access customer features

3. **Test Concurrent Access**:
   - Switch between tabs
   - Verify each maintains its own session
   - Test admin-only features in admin tab
   - Test customer features in customer tab

## Technical Details

### Session Management

The system uses a custom session management approach:

```python
# Role-specific session cookies
session_admin_username = {
    'user_id': 'admin1',
    'user_role': 'admin',
    'user_name': 'Admin User',
    '_created': timestamp
}

session_customer_username = {
    'user_id': 'john_doe',
    'user_role': 'customer',
    'user_name': 'John Doe',
    '_created': timestamp
}
```

### API Endpoints

- **General login**: `/api/auth/login`
- **Admin login**: `/api/auth/login/admin`
- **Customer login**: `/api/auth/login/customer`
- **Session status**: `/api/auth/status`
- **Logout**: `/api/auth/logout`

### Security Features

- Session expiration (24 hours)
- Role-based access control
- Secure cookie settings
- CSRF protection via SameSite cookies

## Troubleshooting

### Common Issues

1. **Sessions not persisting**:
   - Check browser cookie settings
   - Ensure cookies are enabled
   - Try clearing browser cache

2. **Login fails**:
   - Verify backend server is running
   - Check credentials in `data/banking_customers.csv`
   - Review server logs for errors

3. **Admin access denied**:
   - Ensure user has `account_type: 'admin'` in CSV
   - Check session role is correctly set

### Debug Mode

Enable debug logging by setting `debug: true` in `BE/config/config.json`:

```json
{
  "app": {
    "debug": true
  }
}
```

## Browser Compatibility

Tested and working with:
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Security Notes

⚠️ **Important**: This is a demo system for testing purposes. In production:

- Use proper session serialization (not `eval()`)
- Implement secure session storage
- Add rate limiting
- Use HTTPS
- Implement proper password hashing
- Add session rotation

## Support

If you encounter issues:

1. Check the server logs in the terminal
2. Verify all files are in the correct locations
3. Ensure the backend server is running
4. Try the automated test script
5. Clear browser cookies and cache

---

**Happy testing! 🎉** 