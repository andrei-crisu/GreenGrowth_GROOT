"""Instructions for enabling Cloud Firestore API.

This script provides step-by-step instructions for enabling the Firestore API
in your Google Cloud project.
"""
import webbrowser
import os

def print_instructions():
    print("=" * 70)
    print("ENABLE CLOUD FIRESTORE API INSTRUCTIONS")
    print("=" * 70)
    print()
    print("Your Firebase service account key is working correctly!")
    print("However, the Cloud Firestore API is not enabled for your project.")
    print()
    print("PROJECT INFORMATION:")
    print("   • Project ID: groot-f61e8")
    print("   • Service Account: firebase-adminsdk-fbsvc@groot-f61e8.iam.gserviceaccount.com")
    print("   • API to Enable: Cloud Firestore API")
    print()
    print("STEP 1: Enable Cloud Firestore API")
    print("   • Click the link below to open Google Cloud Console")
    print("   • Make sure you're logged in with the correct Google account")
    print("   • Click 'Enable API' button")
    print()
    
    # Create the activation URL
    activation_url = "https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project=groot-f61e8"
    print(f"   🔗 Activation URL: {activation_url}")
    print()
    
    print("STEP 2: Wait for API Activation")
    print("   • After enabling, wait 2-5 minutes for the API to propagate")
    print("   • The activation may take a few minutes to take effect")
    print()
    
    print("STEP 3: Test the Connection")
    print("   • Run: python test_firebase_init.py")
    print("   • You should see: 'Firebase initialized OK' without errors")
    print()
    
    print("ALTERNATIVE: Enable via Firebase Console")
    print("   • Go to: https://console.firebase.google.com/project/groot-f61e8")
    print("   • Click on 'Firestore Database' in the left sidebar")
    print("   • Click 'Create database' if prompted")
    print("   • Choose 'Start in test mode' for development")
    print()
    
    print("VERIFICATION:")
    print("   • After enabling, run: python test_firebase_init.py")
    print("   • Expected output:")
    print("     - 'Firebase initialized OK, firestore client created: True'")
    print("     - 'Collections count (top-level): X' (where X is a number)")
    print("     - No 403 SERVICE_DISABLED errors")
    print()
    
    print("=" * 70)
    
    # Ask if user wants to open the URL
    try:
        response = input("Would you like to open the API activation page now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("Opening Google Cloud Console...")
            webbrowser.open(activation_url)
            print("✅ Opened in your default browser")
        else:
            print("You can manually visit the URL when ready.")
    except KeyboardInterrupt:
        print("\nYou can manually visit the URL when ready.")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print("Please manually visit the URL above.")

if __name__ == "__main__":
    print_instructions()
