# Firebase Tests

This folder contains all Firebase-related test scripts and utilities for the Green Growth - GROOT project.

## Test Files

### Core Integration Tests
- **`test_realtime_db_integration.py`** - Comprehensive test suite for Firebase Realtime Database integration
  - Tests Firebase connection
  - Tests SensorDataReader class
  - Tests API endpoints
  - Run: `python tests/test_realtime_db_integration.py`

- **`test_web_interface.py`** - Tests the web interface with Firebase integration
  - Tests /firebase-data route
  - Tests main dashboard
  - Run: `python tests/test_web_interface.py`

### Firebase Initialization Tests
- **`test_firebase_init.py`** - Basic Firebase initialization test
  - Tests Firebase Admin SDK initialization
  - Tests Firestore client creation
  - Run: `python tests/test_firebase_init.py`

- **`test_firebase_env.py`** - Environment variable test
  - Tests FIREBASE_SERVICE_ACCOUNT_PATH environment variable
  - Run: `python tests/test_firebase_env.py`

### Diagnostic Tools
- **`diagnose_firebase_access.py`** - Comprehensive Firebase access diagnosis
  - Checks environment configuration
  - Validates service account key
  - Tests Firebase connection
  - Analyzes errors and provides solutions
  - Run: `python tests/diagnose_firebase_access.py`

- **`validate_new_firebase_key.py`** - Validates new Firebase service account keys
  - Checks JSON format
  - Validates private key
  - Tests Firebase initialization
  - Run: `python validate_new_firebase_key.py`

### Utility Scripts
- **`enable_firestore_api.py`** - Instructions for enabling Firestore API
  - Provides step-by-step instructions
  - Opens activation URLs
  - Run: `python tests/enable_firestore_api.py`

## Running Tests

### Run All Tests
```bash
cd WebUI/firebase-flask-app
python tests/test_realtime_db_integration.py
python tests/test_web_interface.py
```

### Run Individual Tests
```bash
# Test Firebase connection
python tests/test_firebase_init.py

# Test environment variables
python tests/test_firebase_env.py

# Diagnose Firebase issues
python tests/diagnose_firebase_access.py

# Validate new Firebase key
python tests/validate_new_firebase_key.py
```

## Test Requirements

All tests require:
- Python 3.7+
- Firebase Admin SDK installed
- Valid Firebase service account key
- Environment variables set:
  - `FIREBASE_SERVICE_ACCOUNT_PATH=./config/firebase-key.json`
  - `FIREBASE_DATABASE_URL=https://groot-f61e8-default-rtdb.europe-west1.firebasedatabase.app/`

## Troubleshooting

If tests fail:
1. Check environment variables are set correctly
2. Verify Firebase service account key is valid
3. Ensure Firebase Realtime Database is accessible
4. Run diagnostic tools for detailed error analysis

## File Organization

- **Core tests**: Integration and web interface tests
- **Init tests**: Basic Firebase initialization tests
- **Diagnostic tools**: Problem-solving and validation scripts
- **Utilities**: Helper scripts and instructions
