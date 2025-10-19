from flask import Blueprint, jsonify, request
from app.firebase_client import get_db
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

@api_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product in Firestore."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        db = get_db()
        
        # If Firebase is not available, return mock success
        if db is None:
            return jsonify({
                'success': True,
                'message': 'Product created successfully (test mode - not saved to database)',
                'id': 'test-id-' + str(hash(str(data)))
            }), 201
        
        doc_ref = db.collection('products').add(data)
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'id': doc_ref[1].id
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    try:
        db = get_db()
        
        # If Firebase is not available, return mock data
        if db is None:
            return jsonify({
                'success': True,
                'data': {
                    'id': product_id,
                    'name': 'Test Product',
                    'description': 'This is a test product (Firebase not connected)',
                    'price': 99.99
                }
            })
        
        doc_ref = db.collection('products').document(product_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        product_data = doc.to_dict()
        product_data['id'] = doc.id
        
        return jsonify({
            'success': True,
            'data': product_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product by ID."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        db = get_db()
        
        # If Firebase is not available, return mock success
        if db is None:
            return jsonify({
                'success': True,
                'message': 'Product updated successfully (test mode - not saved to database)'
            })
        
        doc_ref = db.collection('products').document(product_id)
        doc_ref.update(data)
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product by ID."""
    try:
        db = get_db()
        
        # If Firebase is not available, return mock success
        if db is None:
            return jsonify({
                'success': True,
                'message': 'Product deleted successfully (test mode - not saved to database)'
            })
        
        doc_ref = db.collection('products').document(product_id)
        doc_ref.delete()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Sensor API endpoints
@api_bp.route('/sensors', methods=['GET'])
def get_sensors():
    """Get current sensor readings."""
    try:
        # Mock sensor data (replace with real sensor readings)
        sensor_data = {
            'temperature': round(random.uniform(20.0, 26.0), 1),
            'humidity': round(random.uniform(45.0, 75.0), 1),
            'luminosity': random.randint(200, 1200),
            'pump_status': 'ON' if random.choice([True, False]) else 'OFF',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

@api_bp.route('/pump', methods=['POST'])
def control_pump():
    """Control pump status."""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Status parameter required'
            }), 400
        
        new_status = data['status'].upper()
        
        if new_status not in ['ON', 'OFF']:
            return jsonify({
                'success': False,
                'error': 'Status must be ON or OFF'
            }), 400
        
        # In a real implementation, this would control the actual pump
        # For now, we'll just return success
        return jsonify({
            'success': True,
            'message': f'Pump turned {new_status} successfully',
            'status': new_status
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Historical sensor data endpoints
@api_bp.route('/sensors/temperature', methods=['GET'])
def get_temperature_data():
    """Get historical temperature data for charts."""
    try:
        # Generate mock historical data
        current_time = int(time.time())
        time_range = request.args.get('range', '6h')
        
        # Calculate time range in seconds
        range_seconds = {
            '1h': 3600,
            '6h': 21600,
            '24h': 86400,
            '7d': 604800
        }.get(time_range, 21600)
        
        # Generate data points
        data_points = 50
        interval = range_seconds // data_points
        
        labels = []
        values = []
        
        for i in range(data_points):
            timestamp = current_time - (data_points - i) * interval
            labels.append(time.strftime('%H:%M', time.localtime(timestamp)))
            
            # Generate realistic temperature data with some variation
            base_temp = 23.0
            variation = random.uniform(-3, 3)
            time_variation = 2 * math.sin(i * 0.2)  # Daily cycle
            temp = base_temp + variation + time_variation
            values.append(round(temp, 1))
        
        # Calculate statistics
        statistics = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'values': values
            },
            'statistics': statistics
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sensors/humidity', methods=['GET'])
def get_humidity_data():
    """Get historical humidity data for charts."""
    try:
        current_time = int(time.time())
        time_range = request.args.get('range', '6h')
        
        range_seconds = {
            '1h': 3600,
            '6h': 21600,
            '24h': 86400,
            '7d': 604800
        }.get(time_range, 21600)
        
        data_points = 50
        interval = range_seconds // data_points
        
        labels = []
        values = []
        
        for i in range(data_points):
            timestamp = current_time - (data_points - i) * interval
            labels.append(time.strftime('%H:%M', time.localtime(timestamp)))
            
            # Generate realistic humidity data
            base_humidity = 60.0
            variation = random.uniform(-10, 10)
            time_variation = 5 * math.sin(i * 0.15)  # Daily cycle
            humidity = base_humidity + variation + time_variation
            humidity = max(0, min(100, humidity))  # Clamp between 0-100
            values.append(round(humidity, 1))
        
        statistics = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'values': values
            },
            'statistics': statistics
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sensors/luminosity', methods=['GET'])
def get_luminosity_data():
    """Get historical luminosity data for charts."""
    try:
        current_time = int(time.time())
        time_range = request.args.get('range', '6h')
        
        range_seconds = {
            '1h': 3600,
            '6h': 21600,
            '24h': 86400,
            '7d': 604800
        }.get(time_range, 21600)
        
        data_points = 50
        interval = range_seconds // data_points
        
        labels = []
        values = []
        
        for i in range(data_points):
            timestamp = current_time - (data_points - i) * interval
            labels.append(time.strftime('%H:%M', time.localtime(timestamp)))
            
            # Generate realistic light data with day/night cycle
            hour = time.localtime(timestamp).tm_hour
            if 6 <= hour <= 18:  # Daytime
                base_light = 800
                variation = random.uniform(-200, 200)
                time_variation = 400 * math.sin((hour - 6) * math.pi / 12)  # Peak at noon
            else:  # Nighttime
                base_light = 50
                variation = random.uniform(-20, 20)
                time_variation = 0
            
            light = base_light + variation + time_variation
            light = max(0, min(2500, light))  # Clamp between 0-2500
            values.append(int(light))
        
        statistics = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'values': values
            },
            'statistics': statistics
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sensors/pump', methods=['GET'])
def get_pump_data():
    """Get historical pump data for charts."""
    try:
        current_time = int(time.time())
        time_range = request.args.get('range', '6h')
        
        range_seconds = {
            '1h': 3600,
            '6h': 21600,
            '24h': 86400,
            '7d': 604800
        }.get(time_range, 21600)
        
        data_points = 12  # Fewer points for pump data
        interval = range_seconds // data_points
        
        labels = []
        on_times = []
        off_times = []
        
        for i in range(data_points):
            timestamp = current_time - (data_points - i) * interval
            labels.append(time.strftime('%H:%M', time.localtime(timestamp)))
            
            # Generate pump activity data
            if random.choice([True, False]):  # 50% chance of being on
                on_time = random.randint(5, 30)  # 5-30 minutes on
                off_time = random.randint(10, 60)  # 10-60 minutes off
            else:
                on_time = 0
                off_time = random.randint(30, 120)  # 30-120 minutes off
            
            on_times.append(on_time)
            off_times.append(off_time)
        
        # Calculate statistics
        total_runtime = sum(on_times)
        cycles = sum(1 for time in on_times if time > 0)
        efficiency = (total_runtime / (total_runtime + sum(off_times))) * 100 if total_runtime > 0 else 0
        
        statistics = {
            'runtimeToday': total_runtime,
            'cyclesToday': cycles,
            'efficiency': round(efficiency, 1),
            'weeklyRuntime': random.randint(20, 50),
            'weeklyCycles': random.randint(50, 150),
            'lastMaintenance': random.randint(1, 30)
        }
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'onTimes': on_times,
                'offTimes': off_times
            },
            'statistics': statistics,
            'status': random.choice(['ON', 'OFF'])
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
