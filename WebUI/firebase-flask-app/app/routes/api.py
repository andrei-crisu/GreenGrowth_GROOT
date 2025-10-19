from flask import Blueprint, jsonify, request
from app.firebase_client import get_db
from app.sensor_data_reader import SensorDataReader
import random
import math
import time
from datetime import datetime, timedelta

def get_time_range_seconds(time_range):
    """Convert time range string to seconds."""
    time_ranges = {
        '5m': 5 * 60,      # 5 minutes
        '10m': 10 * 60,    # 10 minutes
        '1h': 60 * 60,     # 1 hour
        '6h': 6 * 60 * 60, # 6 hours
        '24h': 24 * 60 * 60, # 24 hours
        '7d': 7 * 24 * 60 * 60 # 7 days
    }
    return time_ranges.get(time_range, 6 * 60 * 60)  # Default to 6 hours

def filter_data_by_time_range(data, time_range):
    """Filter data by time range - get last N minutes of actual data from database."""
    if not data:
        return data
    
    # Sort data by timestamp (most recent first)
    sorted_data = sorted(data, key=lambda x: x['timestamp'], reverse=True)
    
    # Calculate how many data points to return based on time range
    cutoff_seconds = get_time_range_seconds(time_range)
    
    # For short time ranges (5m, 10m), get fewer points
    # For longer time ranges, get more points
    if cutoff_seconds <= 10 * 60:  # 10 minutes or less
        max_points = min(20, len(sorted_data))  # Max 20 points for short ranges
    elif cutoff_seconds <= 60 * 60:  # 1 hour or less
        max_points = min(30, len(sorted_data))  # Max 30 points for medium ranges
    else:  # Longer ranges
        max_points = min(50, len(sorted_data))  # Max 50 points for long ranges
    
    # Get the most recent data points
    recent_data = sorted_data[:max_points]
    
    # Sort back to chronological order (oldest first) for chart display
    return sorted(recent_data, key=lambda x: x['timestamp'])

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
                # Get device name from info section first, then fallback to readings
                device_info = device_data.get('info', {})
                device_name = device_info.get('name')
                
                # If no name in info, try to get from latest reading
                if not device_name:
                    readings = device_data.get('readings', {})
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
                    'total_readings': len(device_data.get('readings', {}))
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
        # Get time range and device parameters from request
        time_range = request.args.get('timeRange', '6h')
        device_mac = request.args.get('device', '')
        print(f"DEBUG: Temperature API called with time range: {time_range}, device: {device_mac}")
        db = get_db()
        
        if db is None:
            print("DEBUG: Using mock data for temperature")
            # Return mock data for charts
            import random
            
            # Generate mock temperature data based on time range
            cutoff_seconds = get_time_range_seconds(time_range)
            
            # For short time ranges, generate more frequent data points
            if cutoff_seconds <= 10 * 60:  # 10 minutes or less
                data_points = min(20, max(5, cutoff_seconds // 30))  # 1 point per 30 seconds
            elif cutoff_seconds <= 60 * 60:  # 1 hour or less
                data_points = min(30, max(10, cutoff_seconds // 60))  # 1 point per minute
            else:  # Longer ranges
                data_points = min(50, max(10, cutoff_seconds // 300))  # 1 point per 5 minutes
            
            labels = []
            values = []
            
            for i in range(data_points):
                dt = datetime.now() - timedelta(seconds=cutoff_seconds * (data_points-i-1) / data_points)
                labels.append(dt.strftime('%H:%M'))
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
        
        # If no device specified, use the first available device
        if not device_mac:
            device_mac = list(all_devices.keys())[0]
            print(f"DEBUG: No device specified, using first device: {device_mac}")
        
        # Check if specified device exists
        if device_mac not in all_devices:
            return jsonify({
                'success': False,
                'error': f'Device {device_mac} not found'
            })
        
        # Collect temperature data from the specified device only
        temperature_data = []
        device_data = all_devices[device_mac]
        readings = device_data.get('readings', {})
        print(f"DEBUG: Device {device_mac} has {len(readings)} total readings")
        print(f"DEBUG: Device data keys: {list(device_data.keys())}")
        if readings:
            sample_key = list(readings.keys())[0]
            print(f"DEBUG: Sample reading key: {sample_key}")
            print(f"DEBUG: Sample reading data: {readings[sample_key]}")
        
            for timestamp_key, reading in readings.items():
                if reading.get('temperature') is not None:
                    temperature_data.append({
                        'timestamp': int(timestamp_key),
                        'value': float(reading['temperature']),
                    'device': device_mac
                    })
        
        print(f"DEBUG: Found {len(temperature_data)} temperature readings for device {device_mac}")
        
        # Sort by timestamp
        temperature_data.sort(key=lambda x: x['timestamp'])
        
        # Debug: Show sample data
        if temperature_data:
            sample = temperature_data[0]
            print(f"DEBUG: Sample reading - timestamp: {sample['timestamp']}, value: {sample['value']}")
        else:
            print("DEBUG: No temperature data found for this device!")
        
        # Filter data by time range
        recent_data = filter_data_by_time_range(temperature_data, time_range)
        print(f"DEBUG: After time range filtering ({time_range}): {len(recent_data)} data points")
        
        # If no recent data, use all available data
        if not recent_data and temperature_data:
            recent_data = temperature_data
            print(f"DEBUG: Using fallback data: {len(recent_data)} data points")
        
        # Format for chart
        labels = []
        values = []
        for data_point in recent_data:  # All points in time range
            dt = datetime.fromtimestamp(data_point['timestamp'] / 1000)
            labels.append(dt.strftime('%H:%M'))
            values.append(data_point['value'])
        
        if values:
            stats = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values)
            }
        else:
            stats = {'min': 0, 'max': 0, 'avg': 0}
        
        print(f"DEBUG: Returning chart data - {len(labels)} labels, {len(values)} values")
        if values:
            print(f"DEBUG: Value range: {min(values)} to {max(values)}")
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'values': values
            },
            'statistics': stats
        })
        
    except Exception as e:
        print(f"DEBUG: Error in temperature API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sensors/humidity', methods=['GET'])
def get_humidity_data():
    """Get humidity data for charts."""
    try:
        # Get time range and device parameters from request
        time_range = request.args.get('timeRange', '6h')
        device_mac = request.args.get('device', '')
        print(f"DEBUG: Humidity API called with time range: {time_range}, device: {device_mac}")
        db = get_db()
        
        if db is None:
            print("DEBUG: Using mock data for humidity")
            # Return mock data for charts
            import random
            
            # Generate mock humidity data based on time range
            cutoff_seconds = get_time_range_seconds(time_range)
            
            # For short time ranges, generate more frequent data points
            if cutoff_seconds <= 10 * 60:  # 10 minutes or less
                data_points = min(20, max(5, cutoff_seconds // 30))  # 1 point per 30 seconds
            elif cutoff_seconds <= 60 * 60:  # 1 hour or less
                data_points = min(30, max(10, cutoff_seconds // 60))  # 1 point per minute
            else:  # Longer ranges
                data_points = min(50, max(10, cutoff_seconds // 300))  # 1 point per 5 minutes
            
            labels = []
            values = []
            
            for i in range(data_points):
                dt = datetime.now() - timedelta(seconds=cutoff_seconds * (data_points-i-1) / data_points)
                labels.append(dt.strftime('%H:%M'))
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
        
        # If no device specified, use the first available device
        if not device_mac:
            device_mac = list(all_devices.keys())[0]
            print(f"DEBUG: No device specified, using first device: {device_mac}")
        
        # Check if specified device exists
        if device_mac not in all_devices:
            return jsonify({
                'success': False,
                'error': f'Device {device_mac} not found'
            })
        
        # Collect humidity data from the specified device only
        humidity_data = []
        device_data = all_devices[device_mac]
        readings = device_data.get('readings', {})
        for timestamp_key, reading in readings.items():
            if reading.get('humidity') is not None:
                humidity_data.append({
                    'timestamp': int(timestamp_key),
                    'value': float(reading['humidity']),
                    'device': device_mac
                })
        
        # Sort by timestamp
        humidity_data.sort(key=lambda x: x['timestamp'])
        
        # Filter data by time range
        recent_data = filter_data_by_time_range(humidity_data, time_range)
        
        # If no recent data, use all available data
        if not recent_data and humidity_data:
            recent_data = humidity_data
        
        # Format for chart
        labels = []
        values = []
        for data_point in recent_data:  # All points in time range
            dt = datetime.fromtimestamp(data_point['timestamp'] / 1000)
            labels.append(dt.strftime('%H:%M'))
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

@api_bp.route('/sensors/luminosity', methods=['GET'])
def get_luminosity_data():
    """Get luminosity data for charts."""
    try:
        # Get time range and device parameters from request
        time_range = request.args.get('timeRange', '6h')
        device_mac = request.args.get('device', '')
        print(f"DEBUG: Luminosity API called with time range: {time_range}, device: {device_mac}")
        db = get_db()
        
        if db is None:
            print("DEBUG: Using mock data for luminosity")
            # Return mock data for charts
            import random
            
            # Generate mock luminosity data based on time range
            cutoff_seconds = get_time_range_seconds(time_range)
            
            # For short time ranges, generate more frequent data points
            if cutoff_seconds <= 10 * 60:  # 10 minutes or less
                data_points = min(20, max(5, cutoff_seconds // 30))  # 1 point per 30 seconds
            elif cutoff_seconds <= 60 * 60:  # 1 hour or less
                data_points = min(30, max(10, cutoff_seconds // 60))  # 1 point per minute
            else:  # Longer ranges
                data_points = min(50, max(10, cutoff_seconds // 300))  # 1 point per 5 minutes
            
            labels = []
            values = []
            
            for i in range(data_points):
                dt = datetime.now() - timedelta(seconds=cutoff_seconds * (data_points-i-1) / data_points)
                labels.append(dt.strftime('%H:%M'))
                values.append(round(random.uniform(200.0, 1200.0), 1))
            
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
        
        # If no device specified, use the first available device
        if not device_mac:
            device_mac = list(all_devices.keys())[0]
            print(f"DEBUG: No device specified, using first device: {device_mac}")
        
        # Check if specified device exists
        if device_mac not in all_devices:
            return jsonify({
                'success': False,
                'error': f'Device {device_mac} not found'
            })
        
        # Collect luminosity data from the specified device only
        luminosity_data = []
        device_data = all_devices[device_mac]
        readings = device_data.get('readings', {})
        for timestamp_key, reading in readings.items():
            if reading.get('light_level') is not None:
                luminosity_data.append({
                        'timestamp': int(timestamp_key),
                    'value': float(reading['light_level']),
                    'device': device_mac
                    })
        
        # Sort by timestamp
        luminosity_data.sort(key=lambda x: x['timestamp'])
        
        # Filter data by time range
        recent_data = filter_data_by_time_range(luminosity_data, time_range)
        
        # If no recent data, use all available data
        if not recent_data and luminosity_data:
            recent_data = luminosity_data
        
        # Format for chart
        labels = []
        values = []
        for data_point in recent_data:  # All points in time range
            dt = datetime.fromtimestamp(data_point['timestamp'] / 1000)
            labels.append(dt.strftime('%H:%M'))
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

@api_bp.route('/sensors/pump', methods=['GET'])
def get_pump_data():
    """Get pump data for charts."""
    try:
        # Get time range and device parameters from request
        time_range = request.args.get('timeRange', '6h')
        device_mac = request.args.get('device', '')
        print(f"DEBUG: Pump API called with time range: {time_range}, device: {device_mac}")
        db = get_db()
        
        if db is None:
            print("DEBUG: Using mock data for pump")
            # Return mock data for charts
            import random
            
            # Generate mock pump data based on time range
            cutoff_seconds = get_time_range_seconds(time_range)
            
            # For short time ranges, generate more frequent data points
            if cutoff_seconds <= 10 * 60:  # 10 minutes or less
                data_points = min(20, max(5, cutoff_seconds // 30))  # 1 point per 30 seconds
            elif cutoff_seconds <= 60 * 60:  # 1 hour or less
                data_points = min(30, max(10, cutoff_seconds // 60))  # 1 point per minute
            else:  # Longer ranges
                data_points = min(50, max(10, cutoff_seconds // 300))  # 1 point per 5 minutes
            
            labels = []
            values = []
            
            for i in range(data_points):
                dt = datetime.now() - timedelta(seconds=cutoff_seconds * (data_points-i-1) / data_points)
                labels.append(dt.strftime('%H:%M'))
                # Generate pump status (0 = OFF, 1 = ON)
                values.append(1 if random.choice([True, False]) else 0)
            
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
        
        # If no device specified, use the first available device
        if not device_mac:
            device_mac = list(all_devices.keys())[0]
            print(f"DEBUG: No device specified, using first device: {device_mac}")
        
        # Check if specified device exists
        if device_mac not in all_devices:
            return jsonify({
                'success': False,
                'error': f'Device {device_mac} not found'
            })
        
        # Collect pump data from the specified device only (using pressure as pump indicator)
        pump_data = []
        device_data = all_devices[device_mac]
        readings = device_data.get('readings', {})
        for timestamp_key, reading in readings.items():
            if reading.get('pressure') is not None:
                # Use pressure > 1000 as pump ON indicator
                pump_status = 1 if float(reading['pressure']) > 1000 else 0
                pump_data.append({
                    'timestamp': int(timestamp_key),
                    'value': pump_status,
                    'device': device_mac
                })
        
        # Sort by timestamp
        pump_data.sort(key=lambda x: x['timestamp'])
        
        # Filter data by time range
        recent_data = filter_data_by_time_range(pump_data, time_range)
        
        # If no recent data, use all available data
        if not recent_data and pump_data:
            recent_data = pump_data
        
        # Format for chart
        labels = []
        values = []
        for data_point in recent_data:  # All points in time range
            dt = datetime.fromtimestamp(data_point['timestamp'] / 1000)
            labels.append(dt.strftime('%H:%M'))
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
