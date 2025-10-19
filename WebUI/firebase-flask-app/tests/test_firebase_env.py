from dotenv import load_dotenv
import os

load_dotenv()

p = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
print('FIREBASE_SERVICE_ACCOUNT_PATH =', repr(p))
if p:
    print('Exists:', os.path.exists(p))
    print('Absolute:', os.path.abspath(p))
else:
    print('Environment variable not set.')
