from flask import Flask
from app.firebase_client import init_firebase
from app.routes.web import web_bp
from app.routes.api import api_bp

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Initialize Firebase
    init_firebase()
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
