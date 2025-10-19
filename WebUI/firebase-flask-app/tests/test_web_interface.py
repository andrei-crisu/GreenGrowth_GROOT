"""Test script for the updated web interface."""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_web_interface():
    """Test the web interface with Firebase Realtime Database."""
    print("🌐 Testing Web Interface with Firebase Realtime Database")
    print("=" * 60)
    
    try:
        from app import create_app
        
        # Create Flask app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test the firebase-data route
        with app.test_client() as client:
            print("\n📡 Testing /firebase-data route...")
            
            # Simulate a logged-in session
            with client.session_transaction() as sess:
                sess['logged_in'] = True
                sess['username'] = 'test_user'
                sess['last_activity'] = 1234567890
            
            response = client.get('/firebase-data')
            
            if response.status_code == 200:
                print("✅ /firebase-data route working")
                
                # Check if the response contains the expected data
                response_text = response.get_data(as_text=True)
                
                if "Firebase Realtime Database" in response_text:
                    print("✅ Template updated to show Realtime Database")
                else:
                    print("⚠️  Template might not be updated")
                
                if "Firebase is not initialized" in response_text:
                    print("❌ Still showing Firebase not initialized error")
                    return False
                else:
                    print("✅ No longer showing Firebase initialization error")
                
                if "User Data:" in response_text:
                    print("✅ Showing user data from Firebase")
                else:
                    print("ℹ️  No user data found (this is normal if no data exists)")
                
                return True
            else:
                print(f"❌ /firebase-data returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing web interface: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_dashboard():
    """Test the main dashboard route."""
    print("\n🏠 Testing Main Dashboard Route")
    print("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Simulate a logged-in session
            with client.session_transaction() as sess:
                sess['logged_in'] = True
                sess['username'] = 'test_user'
                sess['last_activity'] = 1234567890
            
            response = client.get('/')
            
            if response.status_code == 200:
                print("✅ Main dashboard route working")
                
                response_text = response.get_data(as_text=True)
                
                if "firebase_realtime_db" in response_text or "mock_data" in response_text:
                    print("✅ Dashboard showing sensor data")
                else:
                    print("ℹ️  Dashboard might be showing default data")
                
                return True
            else:
                print(f"❌ Main dashboard returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing main dashboard: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 WEB INTERFACE TEST")
    print("=" * 70)
    
    # Test web interface
    web_test = test_web_interface()
    dashboard_test = test_main_dashboard()
    
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    if web_test and dashboard_test:
        print("🎉 All web interface tests passed!")
        print("\nThe error message should no longer appear in your web app.")
        print("You can now:")
        print("1. Start your Flask app: python run.py")
        print("2. Navigate to http://localhost:5000/firebase-data")
        print("3. You should see your real ESP32 sensor data instead of the error message")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return web_test and dashboard_test

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
