"""Comprehensive Firebase service account key repair script.

This script will:
1. Load the existing firebase-key.json
2. Validate the private key format
3. Fix common corruption issues
4. Regenerate the key with proper PEM formatting
5. Create a backup before making changes

Run:
    python fix_firebase_key_comprehensive.py
"""
import json
import os
import base64
import re
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def fix_private_key_format(private_key_str):
    """Fix common issues with private key formatting."""
    print("Original private_key length:", len(private_key_str))
    
    # Remove any surrounding quotes
    if private_key_str.startswith('"') and private_key_str.endswith('"'):
        private_key_str = private_key_str[1:-1]
        print("Removed surrounding quotes")
    
    # Fix escaped newlines
    if '\\n' in private_key_str:
        private_key_str = private_key_str.replace('\\n', '\n')
        print("Fixed escaped newlines")
    
    # Ensure proper PEM format
    if not private_key_str.startswith('-----BEGIN PRIVATE KEY-----'):
        print("Adding proper PEM header")
        private_key_str = '-----BEGIN PRIVATE KEY-----\n' + private_key_str
    
    if not private_key_str.endswith('-----END PRIVATE KEY-----'):
        print("Adding proper PEM footer")
        private_key_str = private_key_str + '\n-----END PRIVATE KEY-----'
    
    # Clean up any extra whitespace
    private_key_str = private_key_str.strip()
    
    print("Fixed private_key length:", len(private_key_str))
    return private_key_str

def validate_private_key(private_key_str):
    """Validate that the private key can be loaded."""
    try:
        # Try to load the private key
        private_key = serialization.load_pem_private_key(
            private_key_str.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        print("✓ Private key validation successful")
        return True
    except Exception as e:
        print(f"✗ Private key validation failed: {e}")
        return False

def regenerate_private_key():
    """Generate a new RSA private key (for testing purposes)."""
    print("Generating new RSA private key...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Serialize to PEM format
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    return pem_private_key.decode('utf-8')

def main():
    key_file = os.path.join('config', 'firebase-key.json')
    backup_file = key_file + '.backup'
    
    if not os.path.exists(key_file):
        print(f"File not found: {key_file}")
        return False
    
    # Create backup
    with open(key_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"Backup created: {backup_file}")
    
    # Load JSON
    try:
        with open(key_file, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return False
    
    original_private_key = key_data.get('private_key', '')
    
    # Try to fix the existing key
    fixed_private_key = fix_private_key_format(original_private_key)
    
    # Validate the fixed key
    if validate_private_key(fixed_private_key):
        print("✓ Successfully fixed the private key")
        key_data['private_key'] = fixed_private_key
    else:
        print("✗ Could not fix the existing private key")
        print("⚠️  WARNING: The private key appears to be corrupted.")
        print("   You will need to regenerate a new service account key from Firebase Console:")
        print("   1. Go to Firebase Console > Project Settings > Service Accounts")
        print("   2. Generate a new private key")
        print("   3. Replace the current firebase-key.json with the new one")
        return False
    
    # Save the fixed key
    try:
        with open(key_file, 'w', encoding='utf-8') as f:
            json.dump(key_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Fixed key saved to {key_file}")
        return True
    except Exception as e:
        print(f"✗ Failed to save fixed key: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Firebase key fix completed successfully!")
        print("Now run: python test_firebase_init.py")
    else:
        print("\n❌ Firebase key fix failed!")
        print("You may need to regenerate the service account key from Firebase Console.")
