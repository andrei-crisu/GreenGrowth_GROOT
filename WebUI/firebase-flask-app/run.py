#!/usr/bin/env python3
"""
Development server entry point for Firebase Flask App.
Run this file to start the development server.
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment variables
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')  # Changed to 0.0.0.0 for network access
    
    print(f"Starting Green Growth - GROOT...")
    print(f"Environment: {'Development' if debug else 'Production'}")
    print(f"Local access: http://127.0.0.1:{port}")
    print(f"Network access: http://[YOUR_IP]:{port}")
    print(f"Debug mode: {'ON' if debug else 'OFF'}")
    
    # Run the development server
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
