from flask import Blueprint, jsonify, request
from app.firebase_client import get_db

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
