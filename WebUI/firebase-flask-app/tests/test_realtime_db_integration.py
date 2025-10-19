"""Test script for Firebase Realtime Database integration.

This script tests the integration between the Flask app and Firebase Realtime Database.
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_firebase_connection():
    """Test Firebase Realtime Database connection."""
    print("🔍 Testing Firebase Realtime Database Connection")
    print("=" * 60)
    
    try:
        from app.firebase_client import init_firebase, get_db, get_database_url
        
        # Initialize Firebase
        init_firebase()
        
        # Get database reference
        db = get_db()
        database_url = get_database_url()
        
        if db is None:
            print("❌ Firebase not initialized")
            return False
        
        print(f"✅ Firebase initialized successfully")
        print(f"📡 Database URL: {database_url}")
        
        # Test basic database access
        try:
            # Try to read from the root
            ref = db.child('test_data')
            data = ref.get()
            
            if data:
                print(f"✅ Successfully connected to Realtime Database")
                print(f"📊 Found test_data with {len(data)} users")
                
                # Show first user's data
                first_user = list(data.keys())[0]
                user_data = data[first_user]
                print(f"👤 First user: {first_user} ({len(user_data)} readings)")
                
                return True
            else:
                print("ℹ️  Connected to database but no test_data found")
                print("   This is normal if no ESP32 data has been sent yet")
                return True
                
        except Exception as e:
            print(f"❌ Error accessing database: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        return False

def test_sensor_data_reader():
    """Test the SensorDataReader class."""
    print("\n🔍 Testing SensorDataReader Class")
    print("=" * 60)
    
    try:
        from app.sensor_data_reader import SensorDataReader
        
        reader = SensorDataReader()
        print("✅ SensorDataReader initialized successfully")
        
        # Test getting all test data
        print("\n📊 Testing get_all_test_data()...")
        all_data = reader.get_all_test_data()
        
        if all_data:
            print(f"✅ Retrieved data for {len(all_data)} users")
            
            # Test getting data for first user
            first_user = list(all_data.keys())[0]
            print(f"\n👤 Testing get_user_data() for user: {first_user}")
            user_data = reader.get_user_data(first_user)
            
            if user_data:
                print(f"✅ Retrieved {len(user_data)} readings for user")
                
                # Test getting latest readings
                print(f"\n⏰ Testing get_latest_readings()...")
                latest_readings = reader.get_latest_readings(first_user, limit=5)
                print(f"✅ Retrieved {len(latest_readings)} latest readings")
                
                # Test sensor summary
                print(f"\n📈 Testing get_sensor_summary()...")
                summary = reader.get_sensor_summary(first_user)
                print(f"✅ Generated summary:")
                print(f"   - Total readings: {summary.get('total_readings', 0)}")
                print(f"   - Devices: {summary.get('device_count', 0)}")
                print(f"   - Latest temp: {summary.get('latest_temperature', 'N/A')}°C")
                print(f"   - Latest humidity: {summary.get('latest_humidity', 'N/A')}%")
                
                return True
            else:
                print("ℹ️  No user data found")
                return True
        else:
            print("ℹ️  No test data found - this is normal if no ESP32 data exists yet")
            return True
            
    except Exception as e:
        print(f"❌ Error testing SensorDataReader: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test the API endpoints."""
    print("\n🔍 Testing API Endpoints")
    print("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test the main sensors endpoint
            print("📡 Testing /api/sensors endpoint...")
            response = client.get('/api/sensors')
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print("✅ /api/sensors endpoint working")
                    sensor_data = data.get('data', {})
                    print(f"   - Temperature: {sensor_data.get('temperature', 'N/A')}°C")
                    print(f"   - Humidity: {sensor_data.get('humidity', 'N/A')}%")
                    print(f"   - Source: {sensor_data.get('source', 'N/A')}")
                else:
                    print(f"⚠️  /api/sensors returned error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ /api/sensors returned status {response.status_code}")
            
            # Test Firebase-specific endpoint
            print("\n📡 Testing /api/sensors/firebase endpoint...")
            response = client.get('/api/sensors/firebase')
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print("✅ /api/sensors/firebase endpoint working")
                    print(f"   - Data count: {data.get('count', 0)}")
                    print(f"   - User UID: {data.get('user_uid', 'N/A')}")
                else:
                    print(f"⚠️  /api/sensors/firebase returned error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ /api/sensors/firebase returned status {response.status_code}")
            
            # Test summary endpoint
            print("\n📡 Testing /api/sensors/summary endpoint...")
            response = client.get('/api/sensors/summary')
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print("✅ /api/sensors/summary endpoint working")
                    summary = data.get('data', {})
                    print(f"   - Total readings: {summary.get('total_readings', 0)}")
                    print(f"   - Device count: {summary.get('device_count', 0)}")
                else:
                    print(f"⚠️  /api/sensors/summary returned error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ /api/sensors/summary returned status {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 FIREBASE REALTIME DATABASE INTEGRATION TEST")
    print("=" * 70)
    print()
    
    # Check environment
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    database_url = os.getenv('FIREBASE_DATABASE_URL', 'https://groot-f61e8-default-rtdb.europe-west1.firebasedatabase.app/')
    
    print(f"🔧 Environment Configuration:")
    print(f"   - Service Account Path: {service_account_path}")
    print(f"   - Database URL: {database_url}")
    print()
    
    # Run tests
    tests = [
        ("Firebase Connection", test_firebase_connection),
        ("SensorDataReader Class", test_sensor_data_reader),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print(f"{'='*70}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Firebase Realtime Database integration is working correctly.")
        print("\nYou can now:")
        print("1. Start your Flask app: python run.py")
        print("2. Access the web interface at http://localhost:5000")
        print("3. Use the API endpoints to get sensor data")
        print("4. Send data from your ESP32 to Firebase Realtime Database")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
