#!/usr/bin/env python3
"""
Firebase Connection Fix Script

This script helps diagnose and fix Firebase connection issues that cause
the system to fall back to mock data instead of using real database data.

Run this script to:
1. Check if Firebase key exists and is valid
2. Test Firebase connection
3. Provide instructions to fix any issues
"""

import os
import json
import sys
from pathlib import Path

def check_firebase_key():
    """Check if Firebase key exists and is valid."""
    print("🔍 Checking Firebase service account key...")
    
    key_path = Path("config/firebase-key.json")
    
    if not key_path.exists():
        print("❌ Firebase key file not found at config/firebase-key.json")
        print("\n📋 To fix this:")
        print("1. Go to Firebase Console: https://console.firebase.google.com/")
        print("2. Select your project: groot-f61e8")
        print("3. Go to Project Settings → Service accounts")
        print("4. Click 'Generate new private key'")
        print("5. Download the JSON file and save it as config/firebase-key.json")
        return False
    
    try:
        with open(key_path, 'r') as f:
            key_data = json.load(f)
        
        # Check required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in key_data]
        
        if missing_fields:
            print(f"❌ Firebase key is missing required fields: {missing_fields}")
            return False
        
        if key_data.get('project_id') != 'groot-f61e8':
            print(f"⚠️  Project ID mismatch: expected 'groot-f61e8', got '{key_data.get('project_id')}'")
        
        print("✅ Firebase key file exists and has required fields")
        return True
        
    except json.JSONDecodeError:
        print("❌ Firebase key file is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading Firebase key: {e}")
        return False

def test_firebase_connection():
    """Test Firebase connection."""
    print("\n🧪 Testing Firebase connection...")
    
    try:
        # Import Firebase modules
        import firebase_admin
        from firebase_admin import credentials, db
        
        # Clear any existing apps
        if firebase_admin._apps:
            for app in firebase_admin._apps.values():
                firebase_admin.delete_app(app)
        
        # Initialize Firebase
        key_path = "config/firebase-key.json"
        cred = credentials.Certificate(key_path)
        app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://groot-f61e8-default-rtdb.europe-west1.firebasedatabase.app/'
        })
        
        # Test Realtime Database connection
        ref = db.reference()
        test_data = ref.child('test').get()
        
        print("✅ Firebase connection successful!")
        print("✅ Realtime Database accessible")
        
        # Clean up
        firebase_admin.delete_app(app)
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        print("\n📋 Common fixes:")
        print("1. Check if the Firebase key is valid and not corrupted")
        print("2. Verify the project ID matches 'groot-f61e8'")
        print("3. Ensure the private key is properly formatted")
        print("4. Check your internet connection")
        return False

def test_app_integration():
    """Test the app's Firebase integration."""
    print("\n🔧 Testing app integration...")
    
    try:
        # Add the app directory to Python path
        sys.path.insert(0, '.')
        
        from app.firebase_client import get_db, init_firebase
        
        # Initialize Firebase
        init_firebase()
        
        # Test database connection
        db = get_db()
        if db is None:
            print("❌ App Firebase integration failed - get_db() returned None")
            return False
        
        print("✅ App Firebase integration working")
        return True
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("FIREBASE CONNECTION FIX SCRIPT")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("❌ Please run this script from the WebUI/firebase-flask-app directory")
        return
    
    # Step 1: Check Firebase key
    key_ok = check_firebase_key()
    
    if not key_ok:
        print("\n❌ Firebase key issue detected. Please fix the key file first.")
        return
    
    # Step 2: Test Firebase connection
    connection_ok = test_firebase_connection()
    
    if not connection_ok:
        print("\n❌ Firebase connection failed. Please check the error messages above.")
        return
    
    # Step 3: Test app integration
    integration_ok = test_app_integration()
    
    if not integration_ok:
        print("\n❌ App integration failed. Please check the error messages above.")
        return
    
    print("\n🎉 SUCCESS! Firebase is properly configured and working.")
    print("Your app should now use real database data instead of mock data.")
    print("\nNext steps:")
    print("1. Run your Flask app: python run.py")
    print("2. Check the dashboard - it should show real device data")
    print("3. The first device found will be automatically selected")

if __name__ == "__main__":
    main()
