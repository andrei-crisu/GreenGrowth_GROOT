"""Validate a new Firebase service account key.

This script will validate that the new Firebase key is properly formatted
and can be used to initialize Firebase Admin SDK.

Run after replacing the corrupted key:
    python validate_new_firebase_key.py
"""
import json
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def validate_firebase_key():
    """Validate the Firebase service account key file."""
    key_file = os.path.join('config', 'firebase-key.json')
    
    print("🔍 Validating Firebase service account key...")
    print(f"Key file: {key_file}")
    
    # Check if file exists
    if not os.path.exists(key_file):
        print("❌ Key file not found!")
        return False
    
    # Load and parse JSON
    try:
        with open(key_file, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
        print("✅ JSON file is valid")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Check required fields
    required_fields = [
        'type', 'project_id', 'private_key', 'client_email', 
        'client_id', 'auth_uri', 'token_uri'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in key_data:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields: {', '.join(missing_fields)}")
        return False
    
    print("✅ All required fields present")
    
    # Validate project ID
    expected_project_id = "groot-f61e8"
    if key_data.get('project_id') != expected_project_id:
        print(f"⚠️  Project ID mismatch: expected '{expected_project_id}', got '{key_data.get('project_id')}'")
    else:
        print(f"✅ Project ID correct: {key_data.get('project_id')}")
    
    # Validate private key format
    private_key = key_data.get('private_key', '')
    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
        print("❌ Private key missing proper PEM header")
        return False
    
    if not private_key.endswith('-----END PRIVATE KEY-----'):
        print("❌ Private key missing proper PEM footer")
        return False
    
    print("✅ Private key has proper PEM format")
    
    # Validate private key can be loaded
    try:
        private_key_obj = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        print("✅ Private key is valid and can be loaded")
    except Exception as e:
        print(f"❌ Private key validation failed: {e}")
        return False
    
    # Validate client email format
    client_email = key_data.get('client_email', '')
    if not client_email.endswith('@groot-f61e8.iam.gserviceaccount.com'):
        print(f"⚠️  Client email format unexpected: {client_email}")
    else:
        print(f"✅ Client email format correct: {client_email}")
    
    print("\n🎉 Firebase key validation successful!")
    print("The key is properly formatted and ready to use.")
    return True

def test_firebase_initialization():
    """Test Firebase initialization with the new key."""
    print("\n🧪 Testing Firebase initialization...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Clear any existing apps
        if firebase_admin._apps:
            for app in firebase_admin._apps.values():
                firebase_admin.delete_app(app)
        
        # Initialize Firebase
        key_file = os.path.join('config', 'firebase-key.json')
        cred = credentials.Certificate(key_file)
        app = firebase_admin.initialize_app(cred)
        
        # Test Firestore connection
        db = firestore.client()
        
        print("✅ Firebase Admin SDK initialized successfully")
        print("✅ Firestore client created successfully")
        
        # Test basic Firestore operation
        try:
            collections = list(db.collections())
            print(f"✅ Firestore connection working - found {len(collections)} collections")
        except Exception as e:
            print(f"⚠️  Firestore connection test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FIREBASE KEY VALIDATION SCRIPT")
    print("=" * 60)
    
    # Validate the key file
    if validate_firebase_key():
        # Test Firebase initialization
        if test_firebase_initialization():
            print("\n🎉 SUCCESS: Firebase is ready to use!")
            print("You can now run your Flask application.")
        else:
            print("\n❌ FAILED: Firebase initialization test failed")
    else:
        print("\n❌ FAILED: Key validation failed")
        print("Please check the Firebase Console instructions and try again.")
    
    print("=" * 60)
