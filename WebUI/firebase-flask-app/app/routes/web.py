from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.firebase_client import get_db

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Render the main page."""
    try:
        db = get_db()
        # Example: Get some data from Firestore
        # products_ref = db.collection('products')
        # products = products_ref.limit(10).stream()
        # products_list = [doc.to_dict() for doc in products]
        
        # For now, return empty list
        products_list = []
        
        return render_template('index.html', products=products_list)
    except Exception as e:
        flash(f'Error loading data: {str(e)}', 'error')
        return render_template('index.html', products=[])

@web_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')
