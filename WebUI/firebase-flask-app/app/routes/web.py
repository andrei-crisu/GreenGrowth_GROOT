from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.firebase_client import get_db
from app.sensor_data_reader import sort_readings_by_timestamp
from functools import wraps
import os
import json
import time

web_bp = Blueprint('web', __name__)

def load_users():
    """Load users from environment variables or config file."""
    # Try to load from environment variable first
    users_json = os.getenv('USERS_JSON')
    if users_json:
        try:
            return json.loads(users_json)
        except json.JSONDecodeError:
            pass
    
    # Fallback to individual environment variables
    users = {}
    admin_user = os.getenv('ADMIN_USER')
    admin_pass = os.getenv('ADMIN_PASS')
    if admin_user and admin_pass:
        users[admin_user] = admin_pass
    
    groot_user = os.getenv('GROOT_USER')
    groot_pass = os.getenv('GROOT_PASS')
    if groot_user and groot_pass:
        users[groot_user] = groot_pass
    
    # Add additional users if specified
    for i in range(1, 6):  # Support up to 5 additional users
        user_key = f'USER{i}_NAME'
        pass_key = f'USER{i}_PASS'
        if os.getenv(user_key) and os.getenv(pass_key):
            users[os.getenv(user_key)] = os.getenv(pass_key)
    
    return users

USERS = load_users()

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Enforce session timeout (5 minutes = 300 seconds)
        timeout_seconds = 300
        now = int(time.time())

        if 'logged_in' not in session:
            return redirect(url_for('web.login'))

        last = session.get('last_activity')
        if last is None:
            # No timestamp - force logout
            session.clear()
            flash('Session expired. Please log in again.', 'info')
            return redirect(url_for('web.login'))

        # If now - last > timeout, session expired
        if now - int(last) > timeout_seconds:
            session.clear()
            flash('Session expired due to inactivity. Please log in again.', 'info')
            return redirect(url_for('web.login'))

        # Refresh last_activity timestamp
        session['last_activity'] = now
        return f(*args, **kwargs)
    return decorated_function

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Reload users on each login attempt to catch env var changes
        current_users = load_users()
        if not current_users:
            flash('No valid users configured. Please check environment variables.', 'error')
            return render_template('login.html')
            
        if username in current_users and current_users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            # Set last activity timestamp
            session['last_activity'] = int(time.time())
            flash('Login successful!', 'success')
            return redirect(url_for('web.index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@web_bp.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('web.login'))

@web_bp.route('/')
@login_required
def index():
    """Render the main dashboard page."""
    try:
        from app.sensor_data_reader import SensorDataReader
        
        # Get selected device from query parameters
        selected_device = request.args.get('device', '')
        
        # Try to get real sensor data from Firebase
        db = get_db()
        if db is not None:
            try:
                reader = SensorDataReader()
                
                # Get the most recent reading from selected device or all devices
                all_devices = reader.get_all_devices_data()
                latest_reading = None
                latest_timestamp = 0
                
                if all_devices:
                    if selected_device and selected_device in all_devices:
                        # Get latest reading from selected device only
                        device_data = all_devices[selected_device]
                        readings = device_data.get('readings', {})
                        for timestamp_key, reading in readings.items():
                            try:
                                timestamp_val = int(timestamp_key)
                                if timestamp_val > latest_timestamp:
                                    latest_timestamp = timestamp_val
                                    latest_reading = reading
                            except (ValueError, TypeError):
                                continue
                    else:
                        # Get latest reading from all devices
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
                        'temperature': latest_reading.get('temperature', 0.0),
                        'humidity': latest_reading.get('humidity', 0.0),
                        'luminosity': latest_reading.get('light_level', 0),
                        'pressure': latest_reading.get('pressure', 0.0),
                        'moisture': latest_reading.get('moisture', 0),
                        'pump_status': 'ON' if latest_reading.get('pressure', 0) > 1000 else 'OFF',
                        'mac_address': latest_reading.get('mac_address', 'Unknown'),
                        'device_name': latest_reading.get('device_name', latest_reading.get('mac_address', 'Unknown')),
                        'last_updated': latest_reading.get('timestamp', 'Unknown'),
                        'source': 'firebase_realtime_db'
                    }
                else:
                    # No data found, use default values
                    sensor_data = {
                        'temperature': 0.0,
                        'humidity': 0.0,
                        'luminosity': 0,
                        'pressure': 0.0,
                        'moisture': 0,
                        'pump_status': 'OFF',
                        'mac_address': 'No Device',
                        'device_name': 'No Device',
                        'last_updated': 'No Data Available',
                        'source': 'no_data'
                    }
            except Exception as e:
                # Firebase error, use default values
                sensor_data = {
                    'temperature': 0.0,
                    'humidity': 0.0,
                    'luminosity': 0,
                    'pressure': 0.0,
                    'moisture': 0,
                    'pump_status': 'OFF',
                    'mac_address': 'Error',
                    'device_name': 'Error',
                    'last_updated': f'Error: {str(e)}',
                    'source': 'error'
                }
        else:
            # Firebase not initialized, use mock data
            sensor_data = {
                'temperature': 23.5,
                'humidity': 65.2,
                'luminosity': 850,
                'pressure': 1013.25,
                'moisture': 45,
                'pump_status': 'ON',
                'mac_address': 'MOCK-001',
                'device_name': 'ESP32 Test Device',
                'last_updated': '2025-01-15 14:30:25',
                'source': 'mock_data'
            }
        
        return render_template('index.html', sensor_data=sensor_data)
    except Exception as e:
        flash(f'Error loading sensor data: {str(e)}', 'error')
        # Return default values on error
        default_data = {
            'temperature': 0.0,
            'humidity': 0.0,
            'luminosity': 0,
            'pressure': 0.0,
            'moisture': 0,
            'pump_status': 'OFF',
            'mac_address': 'Error',
            'device_name': 'Error',
            'last_updated': 'Error',
            'source': 'error'
        }
        return render_template('index.html', sensor_data=default_data)

@web_bp.route('/about')
@login_required
def about():
    """Render the about page."""
    return render_template('about.html')


@web_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Render and handle settings updates."""
    if request.method == 'POST':
        # For now store simple preferences in session
        display_name = request.form.get('display_name')
        contact_email = request.form.get('contact_email')
        session['display_name'] = display_name
        session['contact_email'] = contact_email
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('web.settings'))

    # Provide current values from session if available
    prefs = {
        'display_name': session.get('display_name', ''),
        'contact_email': session.get('contact_email', '')
    }
    return render_template('settings.html', prefs=prefs)


@web_bp.route('/assistant', methods=['GET', 'POST'])
@login_required
def assistant():
    """Simple Groot Assistant mock page. Stores conversation in session."""
    convo = session.get('assistant_convo', [])

    if request.method == 'POST':
        user_msg = request.form.get('message', '').strip()
        if user_msg:
            # Append user message
            convo.append({'role': 'user', 'text': user_msg})

            # Mock assistant reply (placeholder for real AI integration)
            reply = f"Groot Assistant: I received your message: '{user_msg}'." 
            convo.append({'role': 'assistant', 'text': reply})
            session['assistant_convo'] = convo
            flash('Message sent to Groot Assistant.', 'info')
        return redirect(url_for('web.assistant'))

    return render_template('assistant.html', convo=convo)


@web_bp.route('/assistant/clear')
@login_required
def assistant_clear():
    session.pop('assistant_convo', None)
    flash('Assistant conversation cleared.', 'info')
    return redirect(url_for('web.assistant'))


@web_bp.route('/firebase-data')
@login_required
def firebase_data():
    """Quick view of Firebase Realtime Database data with device selection."""
    from app.sensor_data_reader import SensorDataReader
    
    # Get query parameters
    selected_device = request.args.get('device', '')
    items_per_page = int(request.args.get('items', 10))  # Default to 10 items per page
    page = int(request.args.get('page', 1))  # Default to page 1
    
    data = {
        'connected': False,
        'collections': [],
        'database_type': 'realtime',
        'available_devices': [],
        'selected_device': selected_device,
        'selected_device_formatted': '',
        'items_per_page': items_per_page,
        'current_page': page,
        'total_pages': 1,
        'total_items': 0
    }

    db = get_db()
    if db is None:
        return render_template('firebase_data.html', data=data)

    try:
        reader = SensorDataReader()
        
        # Get all devices data
        all_devices = reader.get_all_devices_data()
        data['connected'] = True
        
        if all_devices:
            # Get list of available devices with formatted MAC addresses
            from app.sensor_data_reader import format_mac_address
            data['available_devices'] = []
            for mac_address in all_devices.keys():
                formatted_mac = format_mac_address(mac_address)
                data['available_devices'].append({
                    'raw': mac_address,
                    'formatted': formatted_mac
                })
            
            # Format selected device if any
            if selected_device:
                data['selected_device_formatted'] = format_mac_address(selected_device)
            
            # If no device selected, show all devices
            if not selected_device:
                # Convert Realtime Database structure to collections format for display
                for mac_address, device_data in all_devices.items():
                    # Get readings for this device
                    readings = device_data.get('readings', {})
                    
                    # Sort readings by timestamp key (most recent first)
                    sorted_readings = sort_readings_by_timestamp(readings)
                    
                    # Apply pagination
                    start_idx = (page - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    paginated_readings = sorted_readings[start_idx:end_idx]
                    
                    docs = []
                    for timestamp_key, reading in paginated_readings:
                        docs.append({
                            'id': timestamp_key,
                            'data': reader.format_sensor_reading(reading, timestamp_key)
                        })
                    
                    # Format MAC address for display
                    formatted_mac = format_mac_address(mac_address)
                    data['collections'].append({
                        'name': f'Device: {formatted_mac}',
                        'mac_address': mac_address,
                        'formatted_mac': formatted_mac,
                        'docs': docs,
                        'total_readings': len(readings)
                    })
                    
                    # Update pagination info (use first device's total for simplicity)
                    if not data['total_items']:
                        data['total_items'] = len(readings)
                        data['total_pages'] = max(1, (len(readings) + items_per_page - 1) // items_per_page)
            else:
                # Show data for selected device only
                if selected_device in all_devices:
                    device_data = all_devices[selected_device]
                    readings = device_data.get('readings', {})
                    
                    # Sort readings by timestamp key (most recent first)
                    sorted_readings = sort_readings_by_timestamp(readings)
                    
                    # Apply pagination
                    start_idx = (page - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    paginated_readings = sorted_readings[start_idx:end_idx]
                    
                    docs = []
                    for timestamp_key, reading in paginated_readings:
                        docs.append({
                            'id': timestamp_key,
                            'data': reader.format_sensor_reading(reading, timestamp_key)
                        })
                    
                    # Format MAC address for display
                    formatted_mac = format_mac_address(selected_device)
                    data['collections'].append({
                        'name': f'Device: {formatted_mac}',
                        'mac_address': selected_device,
                        'formatted_mac': formatted_mac,
                        'docs': docs,
                        'total_readings': len(readings)
                    })
                    
                    # Update pagination info
                    data['total_items'] = len(readings)
                    data['total_pages'] = max(1, (len(readings) + items_per_page - 1) // items_per_page)
                else:
                    data['error'] = f'Device {selected_device} not found'
        else:
            data['collections'] = []
            
    except Exception as e:
        data['error'] = str(e)

    return render_template('firebase_data.html', data=data)

@web_bp.route('/charts/temperature')
@login_required
def temperature_chart():
    """Render the temperature chart page."""
    return render_template('charts/temperature.html')

@web_bp.route('/charts/humidity')
@login_required
def humidity_chart():
    """Render the humidity chart page."""
    return render_template('charts/humidity.html')

@web_bp.route('/charts/luminosity')
@login_required
def luminosity_chart():
    """Render the luminosity chart page."""
    return render_template('charts/luminosity.html')

@web_bp.route('/charts/pump')
@login_required
def pump_chart():
    """Render the pump status chart page."""
    return render_template('charts/pump.html')
