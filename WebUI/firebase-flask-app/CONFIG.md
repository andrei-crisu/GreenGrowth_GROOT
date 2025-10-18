# 🔐 Configuration Guide - Green Growth - GROOT

## Environment Variables

Create a `.env` file in the `WebUI/firebase-flask-app/` directory with the following variables:

### Required Configuration

```bash
# Flask Configuration
SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Firebase Configuration (Optional)
FIREBASE_SERVICE_ACCOUNT_PATH=path/to/your/service-account-key.json
```

### Authentication Configuration

You have two options for setting up user credentials:

#### Option 1: Individual User Variables (Recommended)

```bash
# Default admin user
ADMIN_USER=admin
ADMIN_PASS=your-secure-admin-password

# GROOT user
GROOT_USER=groot
GROOT_PASS=your-secure-groot-password

# Additional users (optional)
USER1_NAME=john
USER1_PASS=john-secure-password
USER2_NAME=jane
USER2_PASS=jane-secure-password
```

#### Option 2: JSON Format (Advanced)

```bash
# JSON format for multiple users (overrides individual settings)
USERS_JSON={"admin":"secure-password","groot":"another-password","user":"user-password"}
```

## 🔒 Security Best Practices

1. **Never commit `.env` files to version control**
2. **Use strong, unique passwords**
3. **Change default credentials immediately**
4. **Use environment-specific configurations**

## 📝 Example .env File

```bash
# Flask Configuration
SECRET_KEY=my-super-secret-key-2024-groot-system
FLASK_ENV=development
FLASK_DEBUG=True

# Authentication
ADMIN_USER=admin
ADMIN_PASS=MySecureAdminPass123!
GROOT_USER=groot
GROOT_PASS=GrootSecurePass456!

# Firebase (Optional)
FIREBASE_SERVICE_ACCOUNT_PATH=./config/firebase-key.json
```

## 🚀 Quick Setup

1. Copy this configuration to a `.env` file
2. Change all passwords to secure ones
3. Update the SECRET_KEY to a random string
4. Restart the application

## 🔒 Security & Repository

### ✅ What's Protected
- **`.env` files** are excluded from the repository
- **Firebase keys** are ignored
- **All credentials** are environment-based
- **No sensitive data** in source code

### 📁 Files Excluded from Git
```
.env
.env.local
.env.production
.env.staging
firebase-*.json
service-account-*.json
*.key
*.pem
*.p12
*.pfx
*.crt
*.cer
config.json
secrets.json
credentials.json
```

## 🔧 Default Credentials (Development Only)

If no `.env` file is found, the system uses these defaults:
- **admin** / **admin**
- **groot** / **groot123**

**⚠️ WARNING: Change these defaults in production!**

## 🛡️ Security Checklist

- [ ] Create `.env` file with secure credentials
- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Verify `.env` is in `.gitignore`
- [ ] Never commit credentials to repository
- [ ] Use environment-specific configurations
