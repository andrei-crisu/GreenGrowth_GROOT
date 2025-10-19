import os
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variables for Firebase clients
rtdb = None
cred = None
database_url = None

def init_firebase():
    """Initialize Firebase Admin SDK and Realtime Database client."""
    global rtdb, cred, database_url
    
    try:
        # Get Firebase service account key from environment
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        database_url = os.getenv('FIREBASE_DATABASE_URL', 'https://groot-f61e8-default-rtdb.europe-west1.firebasedatabase.app/')
        
        # If not set via environment, try to use the local file
        if not service_account_path:
            local_key_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'firebase-key.json')
            if os.path.exists(local_key_path):
                service_account_path = local_key_path
                print(f"Using local Firebase key: {service_account_path}")
            else:
                print("FIREBASE_SERVICE_ACCOUNT_PATH not set and no local key found - running in test mode without Firebase")
                rtdb = None
                return
        
        # Initialize Firebase Admin SDK with Realtime Database URL
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
        
        # Get Realtime Database reference
        rtdb = db.reference()
        
        print(f"Firebase Realtime Database initialized successfully")
        print(f"Database URL: {database_url}")
        
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        print("Continuing in test mode without Firebase")
        rtdb = None

def get_db():
    """Get Realtime Database reference."""
    if rtdb is None:
        print("Warning: Firebase not initialized - running in test mode")
        return None
    return rtdb

def get_database_url():
    """Get the database URL."""
    return database_url
