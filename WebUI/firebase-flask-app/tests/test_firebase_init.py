from dotenv import load_dotenv
import os

load_dotenv()

p = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
print('Using key at:', p)
print('Exists:', os.path.exists(p))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        cred = credentials.Certificate(p)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print('Firebase initialized OK, firestore client created:', db is not None)
    try:
        cols = list(db.collections())
        print('Collections count (top-level):', len(cols))
        for c in cols[:5]:
            print(' -', c.id)
    except Exception as e:
        print('Error listing collections:', e)
except Exception as e:
    print('Firebase init error:', e)
