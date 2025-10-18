import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variables for Firebase clients
db = None
cred = None

def init_firebase():
    """Initialize Firebase Admin SDK and Firestore client."""
    global db, cred
    
    try:
        # Get Firebase service account key from environment
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        
        if not service_account_path:
            print("FIREBASE_SERVICE_ACCOUNT_PATH not set - running in test mode without Firebase")
            db = None
            return
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        
        # Initialize Firestore client
        db = firestore.client()
        
        print("Firebase initialized successfully")
        
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        print("Continuing in test mode without Firebase")
        db = None

def get_db():
    """Get Firestore database client."""
    if db is None:
        print("Warning: Firebase not initialized - running in test mode")
        return None
    return db
