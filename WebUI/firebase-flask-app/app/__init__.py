from flask import Flask, session
from app.firebase_client import init_firebase
from app.routes.web import web_bp
from app.routes.api import api_bp
import os

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Set secret key for sessions
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Initialize Firebase
    init_firebase()
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
