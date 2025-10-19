from flask import Blueprint, jsonify, request
from app.firebase_client import get_db
from app.sensor_data_reader import SensorDataReader
import random
import math
import time
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products from Firestore."""
    try:
        db = get_db()
        
        # If Firebase is not available, return empty list
        if db is None:
            return jsonify({
                'success': True,
                'data': [],
                'count': 0,
                'message': 'Running in test mode - no Firebase connection'
            })
        
        products_ref = db.collection('products')
        products = products_ref.stream()
        
        products_list = []
        for doc in products:
            product_data = doc.to_dict()
            product_data['id'] = doc.id
            products_list.append(product_data)
        
        return jsonify({
            'success': True,
            'data': products_list,
            'count': len(products_list)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/devices', methods=['GET'])
def get_devices():
    """Get all available devices from Firebase Realtime Database."""
    try:
        db = get_db()
        
        # If Firebase is not available, return empty list
        if db is None:
            return jsonify({
                'success': True,
                'devices': []
            })
        
        # Get real device data from Firebase
        reader = SensorDataReader()
        all_devices = reader.get_all_devices_data()
        
        devices = []
        if all_devices:
            for mac_address, device_data in all_devices.items():
                # Get device name from the latest reading
                readings = device_data.get('readings', {})
                device_name = None
                if readings:
                    # Get the latest reading to find device name
                    latest_reading = None
                    latest_timestamp = 0
                    for timestamp_key, reading in readings.items():
                        try:
                            timestamp_val = int(timestamp_key)
                            if timestamp_val > latest_timestamp:
                                latest_timestamp = timestamp_val
                                latest_reading = reading
                        except (ValueError, TypeError):
                            continue
                    
                    if latest_reading:
                        device_name = latest_reading.get('device_name')
                
                devices.append({
                    'mac_address': mac_address,
                    'device_name': device_name or mac_address,
                    'total_readings': len(readings)
                })
        
        return jsonify({
            'success': True,
            'devices': devices
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Sensor API endpoints
@api_bp.route('/sensors', methods=['GET'])
def get_sensors():
    """Get current sensor readings from Firebase Realtime Database."""
    try:
        db = get_db()

        # If Firebase is not available, return mock data
        if db is None:
            sensor_data = {
                'temperature': round(random.uniform(20.0, 26.0), 1),
                'humidity': round(random.uniform(45.0, 75.0), 1),
                'luminosity': random.randint(200, 1200),
                'pressure': round(random.uniform(1000.0, 1030.0), 1),
                'moisture': random.randint(20, 80),
                'pump_status': 'ON' if random.choice([True, False]) else 'OFF',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'mock_data'
            }

            return jsonify({
                'success': True,
                'data': sensor_data
            })

        # Get real sensor data from Firebase
        reader = SensorDataReader()

        # Get all devices data to find the most recent reading
        all_devices = reader.get_all_devices_data()
        print(f"DEBUG: Retrieved {len(all_devices) if all_devices else 0} devices from Firebase")

        if not all_devices:
            print("DEBUG: No devices found in Firebase")
            return jsonify({
                'success': True,
                'data': {
                    'temperature': None,
                    'humidity': None,
                    'luminosity': None,
                    'pressure': None,
                    'moisture': None,
                    'mac_address': None,
                    'timestamp': None,
                    'source': 'no_data'
                },
                'message': 'No sensor data available'
            })

        # Find the most recent reading across all devices
        latest_reading = None
        latest_timestamp = 0

        for mac_address, device_data in all_devices.items():
            readings = device_data.get('readings', {})
            for timestamp_key, reading in readings.items():
                try:
                    timestamp_val = int(timestamp_key)
                    if timestamp_val > latest_timestamp:
                        latest_timestamp = timestamp_val
                        latest_reading = reading
                except (ValueError, TypeError):
                    continue

        if latest_reading:
            sensor_data = {
                'temperature': latest_reading.get('temperature'),
                'humidity': latest_reading.get('humidity'),
                'luminosity': latest_reading.get('light_level'),
                'pressure': latest_reading.get('pressure'),
                'moisture': latest_reading.get('moisture'),
                'mac_address': latest_reading.get('mac_address'),
                'timestamp': latest_reading.get('timestamp'),
                'source': 'firebase_realtime_db'
            }
            print(f"DEBUG: Latest reading found - Temp: {sensor_data['temperature']}, Humidity: {sensor_data['humidity']}")
        else:
            print("DEBUG: No latest reading found")
            sensor_data = {
                'temperature': None,
                'humidity': None,
                'luminosity': None,
                'pressure': None,
                'moisture': None,
                'mac_address': None,
                'timestamp': None,
                'source': 'no_valid_data'
            }

        return jsonify({
            'success': True,
            'data': sensor_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sensors/temperature', methods=['GET'])
def get_temperature_data():
    """Get temperature data for charts."""
    try:
        print("DEBUG: Temperature API called")
        db = get_db()
        
        if db is None:
            print("DEBUG: Using mock data for temperature")
            # Return mock data for charts
            import random
            from datetime import datetime, timedelta
            
            # Generate mock temperature data for the last 24 hours
            data_points = 24
            labels = []
            values = []
            
            for i in range(data_points):
                time = datetime.now() - timedelta(hours=data_points-i-1)
                labels.append(time.strftime('%H:%M'))
                values.append(round(random.uniform(20.0, 30.0), 1))
            
            result = {
                'success': True,
                'data': {
                    'labels': labels,
                    'values': values
                },
                'statistics': {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                }
            }
            print(f"DEBUG: Returning mock data with {len(values)} points")
            return jsonify(result)
        
        # Get real data from Firebase
        reader = SensorDataReader()
        all_devices = reader.get_all_devices_data()
        
        if not all_devices:
            return jsonify({
                'success': False,
                'error': 'No data available'
            })
        
        # Collect temperature data from all devices
        temperature_data = []
        for mac_address, device_data in all_devices.items():
            readings = device_data.get('readings', {})
            for timestamp_key, reading in readings.items():
                if reading.get('temperature') is not None:
                    temperature_data.append({
                        'timestamp': int(timestamp_key),
                        'value': float(reading['temperature']),
                        'device': mac_address
                    })
        
        # Sort by timestamp
        temperature_data.sort(key=lambda x: x['timestamp'])
        
        # Get last 24 hours of data
        from datetime import datetime, timedelta
        # Try both seconds and milliseconds for timestamp comparison
        cutoff_time_seconds = int((datetime.now() - timedelta(hours=24)).timestamp())
        cutoff_time_milliseconds = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        current_time_seconds = int(datetime.now().timestamp())
        
        # Try to determine timestamp format by comparing with current time
        sample_timestamp = temperature_data[-1]['timestamp'] if temperature_data else 0
        if sample_timestamp > current_time_seconds:
            # Timestamps are in milliseconds
            cutoff_time = cutoff_time_milliseconds
        else:
            # Timestamps are in seconds
            cutoff_time = cutoff_time_seconds
        
        recent_data = [d for d in temperature_data if d['timestamp'] > cutoff_time]
        
        # If no recent data, use all available data (last 50 points)
        if not recent_data and temperature_data:
            recent_data = temperature_data[-50:]
        
        # Format for chart
        labels = []
        values = []
        for data_point in recent_data[-50:]:  # Last 50 points
            time = datetime.fromtimestamp(data_point['timestamp'] / 1000)
            labels.append(time.strftime('%H:%M'))
            values.append(data_point['value'])
        
        if values:
            stats = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values)
            }
        else:
            stats = {'min': 0, 'max': 0, 'avg': 0}
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'values': values
            },
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sensors/humidity', methods=['GET'])
def get_humidity_data():
    """Get humidity data for charts."""
    try:
        print("DEBUG: Humidity API called")
        db = get_db()
        
        if db is None:
            print("DEBUG: Using mock data for humidity")
            # Return mock data for charts
            import random
            from datetime import datetime, timedelta
            
            # Generate mock humidity data for the last 24 hours
            data_points = 24
            labels = []
            values = []
            
            for i in range(data_points):
                time = datetime.now() - timedelta(hours=data_points-i-1)
                labels.append(time.strftime('%H:%M'))
                values.append(round(random.uniform(40.0, 80.0), 1))
            
            result = {
                'success': True,
                'data': {
                    'labels': labels,
                    'values': values
                },
                'statistics': {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                }
            }
            print(f"DEBUG: Returning mock data with {len(values)} points")
            return jsonify(result)
        
        # Get real data from Firebase
        reader = SensorDataReader()
        all_devices = reader.get_all_devices_data()
        
        if not all_devices:
            return jsonify({
                'success': False,
                'error': 'No data available'
            })
        
        # Collect humidity data from all devices
        humidity_data = []
        for mac_address, device_data in all_devices.items():
            readings = device_data.get('readings', {})
            for timestamp_key, reading in readings.items():
                if reading.get('humidity') is not None:
                    humidity_data.append({
                        'timestamp': int(timestamp_key),
                        'value': float(reading['humidity']),
                        'device': mac_address
                    })
        
        # Sort by timestamp
        humidity_data.sort(key=lambda x: x['timestamp'])
        
        # Get last 24 hours of data
        from datetime import datetime, timedelta
        # Try both seconds and milliseconds for timestamp comparison
        cutoff_time_seconds = int((datetime.now() - timedelta(hours=24)).timestamp())
        cutoff_time_milliseconds = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        current_time_seconds = int(datetime.now().timestamp())
        
        # Try to determine timestamp format by comparing with current time
        sample_timestamp = humidity_data[-1]['timestamp'] if humidity_data else 0
        if sample_timestamp > current_time_seconds:
            # Timestamps are in milliseconds
            cutoff_time = cutoff_time_milliseconds
        else:
            # Timestamps are in seconds
            cutoff_time = cutoff_time_seconds
        
        recent_data = [d for d in humidity_data if d['timestamp'] > cutoff_time]
        
        # If no recent data, use all available data (last 50 points)
        if not recent_data and humidity_data:
            recent_data = humidity_data[-50:]
        
        # Format for chart
        labels = []
        values = []
        for data_point in recent_data[-50:]:  # Last 50 points
            time = datetime.fromtimestamp(data_point['timestamp'] / 1000)
            labels.append(time.strftime('%H:%M'))
            values.append(data_point['value'])
        
        if values:
            stats = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values)
            }
        else:
            stats = {'min': 0, 'max': 0, 'avg': 0}
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'values': values
            },
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint."""
    return jsonify({
        'success': True,
        'message': 'API is working',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/pump', methods=['POST'])
def toggle_pump():
    """Toggle pump status."""
    try:
        data = request.get_json()
        new_status = data.get('status', 'OFF')
        
        # In a real implementation, this would control the actual pump
        # For now, we'll just return success
        
        return jsonify({
            'success': True,
            'message': f'Pump turned {new_status}',
            'pump_status': new_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
