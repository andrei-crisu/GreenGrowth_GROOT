from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.firebase_client import get_db

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Render the main dashboard page."""
    try:
        # Mock sensor data (replace with real sensor readings)
        sensor_data = {
            'temperature': 23.5,
            'humidity': 65.2,
            'luminosity': 850,
            'pump_status': 'ON',
            'last_updated': '2024-01-15 14:30:25'
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
def about():
    """Render the about page."""
    return render_template('about.html')

@web_bp.route('/charts/temperature')
def temperature_chart():
    """Render the temperature chart page."""
    return render_template('charts/temperature.html')

@web_bp.route('/charts/humidity')
def humidity_chart():
    """Render the humidity chart page."""
    return render_template('charts/humidity.html')

@web_bp.route('/charts/luminosity')
def luminosity_chart():
    """Render the luminosity chart page."""
    return render_template('charts/luminosity.html')

@web_bp.route('/charts/pump')
def pump_chart():
    """Render the pump status chart page."""
    return render_template('charts/pump.html')
