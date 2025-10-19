"""Comprehensive Firebase access diagnosis script.

This script will help diagnose why you can't access your Firebase database
even though it exists.
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check environment configuration."""
    print("🔍 ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Check environment variable
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    print(f"FIREBASE_SERVICE_ACCOUNT_PATH: {service_account_path}")
    
    if service_account_path:
        print(f"File exists: {os.path.exists(service_account_path)}")
        if os.path.exists(service_account_path):
            print(f"Absolute path: {os.path.abspath(service_account_path)}")
    else:
        print("❌ Environment variable not set!")
        return False
    
    print()

def check_service_account():
    """Check service account key file."""
    print("🔑 SERVICE ACCOUNT CHECK")
    print("=" * 50)
    
    key_file = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', './config/firebase-key.json')
    
    try:
        with open(key_file, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
        
        print(f"✅ JSON file is valid")
        print(f"Project ID: {key_data.get('project_id')}")
        print(f"Client Email: {key_data.get('client_email')}")
        print(f"Private Key ID: {key_data.get('private_key_id')}")
        
        # Check if private key looks valid
        private_key = key_data.get('private_key', '')
        if private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            print("✅ Private key format looks correct")
        else:
            print("❌ Private key format incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Error reading service account file: {e}")
        return False
    
    print()
    return True

def test_firebase_connection():
    """Test Firebase connection with detailed error reporting."""
    print("🔥 FIREBASE CONNECTION TEST")
    print("=" * 50)
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Clear any existing apps
        if firebase_admin._apps:
            for app in firebase_admin._apps.values():
                firebase_admin.delete_app(app)
        
        # Initialize Firebase
        key_file = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', './config/firebase-key.json')
        cred = credentials.Certificate(key_file)
        app = firebase_admin.initialize_app(cred)
        
        print("✅ Firebase Admin SDK initialized successfully")
        
        # Test Firestore client
        db = firestore.client()
        print("✅ Firestore client created successfully")
        
        # Try to access Firestore
        try:
            print("🔄 Attempting to list collections...")
            collections = list(db.collections())
            print(f"✅ Successfully accessed Firestore - found {len(collections)} collections")
            
            if collections:
                print("Collections found:")
                for i, collection in enumerate(collections[:5]):  # Show first 5
                    print(f"  {i+1}. {collection.id}")
                if len(collections) > 5:
                    print(f"  ... and {len(collections) - 5} more")
            else:
                print("ℹ️  No collections found (database is empty but accessible)")
                
            return True
            
        except Exception as e:
            print(f"❌ Error accessing Firestore: {e}")
            
            # Analyze the error
            error_str = str(e)
            if "SERVICE_DISABLED" in error_str:
                print("\n🔍 DIAGNOSIS: Cloud Firestore API is disabled")
                print("   Solution: Enable the API at the provided URL")
            elif "PERMISSION_DENIED" in error_str:
                print("\n🔍 DIAGNOSIS: Permission denied")
                print("   Solution: Check service account permissions")
            elif "NOT_FOUND" in error_str:
                print("\n🔍 DIAGNOSIS: Project or database not found")
                print("   Solution: Verify project ID and database exists")
            elif "UNAUTHENTICATED" in error_str:
                print("\n🔍 DIAGNOSIS: Authentication failed")
                print("   Solution: Check service account key validity")
            else:
                print(f"\n🔍 DIAGNOSIS: Unknown error - {type(e).__name__}")
                print("   Solution: Check error details above")
            
            return False
            
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False

def check_project_status():
    """Check if we can get project information."""
    print("📊 PROJECT STATUS CHECK")
    print("=" * 50)
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        # Initialize Firebase
        key_file = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', './config/firebase-key.json')
        cred = credentials.Certificate(key_file)
        
        if not firebase_admin._apps:
            app = firebase_admin.initialize_app(cred)
        else:
            app = list(firebase_admin._apps.values())[0]
        
        print(f"✅ Project ID: {app.project_id}")
        print(f"✅ Service Account: {cred.service_account_email}")
        
        # Try to get project info
        try:
            from google.cloud import resourcemanager
            client = resourcemanager.ProjectsClient(credentials=cred)
            project = client.get_project(name=f"projects/{app.project_id}")
            print(f"✅ Project exists: {project.display_name}")
            print(f"✅ Project state: {project.state.name}")
        except Exception as e:
            print(f"⚠️  Could not verify project status: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Could not check project status: {e}")
        return False

def main():
    print("🔍 FIREBASE ACCESS DIAGNOSIS")
    print("=" * 60)
    print()
    
    # Run all checks
    env_ok = check_environment()
    if not env_ok:
        print("❌ Environment check failed - stopping diagnosis")
        return
    
    sa_ok = check_service_account()
    if not sa_ok:
        print("❌ Service account check failed - stopping diagnosis")
        return
    
    project_ok = check_project_status()
    if not project_ok:
        print("⚠️  Project status check failed - continuing anyway")
    
    connection_ok = test_firebase_connection()
    
    print("\n" + "=" * 60)
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if connection_ok:
        print("🎉 SUCCESS: Firebase is working correctly!")
        print("   Your database is accessible and ready to use.")
    else:
        print("❌ ISSUE FOUND: Firebase access is blocked")
        print("\n🔧 POSSIBLE SOLUTIONS:")
        print("1. Enable Cloud Firestore API:")
        print("   https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project=groot-f61e8")
        print()
        print("2. Check service account permissions:")
        print("   https://console.cloud.google.com/iam-admin/iam?project=groot-f61e8")
        print()
        print("3. Verify database exists in Firebase Console:")
        print("   https://console.firebase.google.com/project/groot-f61e8/firestore")
        print()
        print("4. Check if billing is enabled for the project")
        print("5. Wait a few minutes if you just enabled the API")

if __name__ == "__main__":
    main()
