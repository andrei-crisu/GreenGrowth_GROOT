from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.firebase_client import get_db
from functools import wraps
import os
import json

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
    admin_user = os.getenv('ADMIN_USER', 'admin')
    admin_pass = os.getenv('ADMIN_PASS', 'admin')
    users[admin_user] = admin_pass
    
    groot_user = os.getenv('GROOT_USER', 'groot')
    groot_pass = os.getenv('GROOT_PASS', 'groot123')
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
        if 'logged_in' not in session:
            return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
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
        # Mock sensor data (replace with real sensor readings)
        sensor_data = {
            'temperature': 23.5,
            'humidity': 65.2,
            'luminosity': 850,
            'pump_status': 'ON',
            'last_updated': '2025-01-15 14:30:25'
        }
        
        return render_template('index.html', sensor_data=sensor_data)
    except Exception as e:
        flash(f'Error loading sensor data: {str(e)}', 'error')
        # Return default values on error
        default_data = {
            'temperature': 0.0,
            'humidity': 0.0,
            'luminosity': 0,
            'pump_status': 'OFF',
            'last_updated': 'Error'
        }
        return render_template('index.html', sensor_data=default_data)

@web_bp.route('/about')
@login_required
def about():
    """Render the about page."""
    return render_template('about.html')

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
