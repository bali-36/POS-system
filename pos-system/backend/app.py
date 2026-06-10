"""
POS System Flask API Server
REST API endpoints for the Point of Sale system.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database as db
import os

# Get the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the built React app
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


# ============== AUTH ENDPOINTS ==============

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    user = db.get_user_by_username(username)
    if user and user['password'] == password:
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'email': user['email'],
                'role': user['role']
            }
        })
    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401


@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    # Simplified - in production, use JWT tokens
    return jsonify({'success': True})


# ============== USER ENDPOINTS ==============

@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.get_all_users()
    # Don't return passwords
    for user in users:
        user.pop('password', None)
    return jsonify(users)


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        user_id = db.create_user(data)
        return jsonify({'success': True, 'id': user_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    success = db.update_user(user_id, data)
    return jsonify({'success': success})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    success = db.delete_user(user_id)
    return jsonify({'success': success})


# ============== CATEGORY ENDPOINTS ==============

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = db.get_all_categories()
    return jsonify(categories)


@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    try:
        category_id = db.create_category(data)
        return jsonify({'success': True, 'id': category_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.get_json()
    success = db.update_category(category_id, data)
    return jsonify({'success': success})


@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    success = db.delete_category(category_id)
    return jsonify({'success': success})


# ============== PRODUCT ENDPOINTS ==============

@app.route('/api/products', methods=['GET'])
def get_products():
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', None)
    low_stock = request.args.get('low_stock', 'false').lower() == 'true'

    if category_id:
        category_id = int(category_id)

    products = db.get_all_products(
        search=search if search else None,
        category_id=category_id,
        low_stock=low_stock
    )
    return jsonify(products)


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = db.get_product_by_id(product_id)
    if product:
        return jsonify(product)
    return jsonify({'success': False, 'message': 'Product not found'}), 404


@app.route('/api/products/barcode/<barcode>', methods=['GET'])
def get_product_by_barcode(barcode):
    product = db.get_product_by_barcode(barcode)
    if product:
        return jsonify(product)
    return jsonify({'success': False, 'message': 'Product not found'}), 404


@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    try:
        product_id = db.create_product(data)
        return jsonify({'success': True, 'id': product_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    success = db.update_product(product_id, data)
    return jsonify({'success': success})


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    success = db.delete_product(product_id)
    return jsonify({'success': success})


# ============== CUSTOMER ENDPOINTS ==============

@app.route('/api/customers', methods=['GET'])
def get_customers():
    search = request.args.get('search', '')
    customers = db.get_all_customers(search=search if search else None)
    return jsonify(customers)


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.get_customer_by_id(customer_id)
    if customer:
        return jsonify(customer)
    return jsonify({'success': False, 'message': 'Customer not found'}), 404


@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    try:
        customer_id = db.create_customer(data)
        return jsonify({'success': True, 'id': customer_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    success = db.update_customer(customer_id, data)
    return jsonify({'success': success})


@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    success = db.delete_customer(customer_id)
    return jsonify({'success': success})


# ============== ORDER ENDPOINTS ==============

@app.route('/api/orders', methods=['GET'])
def get_orders():
    limit = request.args.get('limit', None)
    offset = request.args.get('offset', 0)
    if limit:
        limit = int(limit)
    orders = db.get_all_orders(limit=limit, offset=int(offset))
    return jsonify(orders)


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = db.get_order_by_id(order_id)
    if order:
        return jsonify(order)
    return jsonify({'success': False, 'message': 'Order not found'}), 404


@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    try:
        order_id = db.create_order(data)
        order = db.get_order_by_id(order_id)
        return jsonify({'success': True, 'order': order}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    success = db.delete_order(order_id)
    return jsonify({'success': success})


# ============== DASHBOARD ENDPOINTS ==============

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    stats = db.get_dashboard_stats()
    return jsonify(stats)


@app.route('/api/dashboard/sales-chart', methods=['GET'])
def get_sales_chart():
    period = request.args.get('period', 'week')
    data = db.get_sales_chart_data(period=period)
    return jsonify(data)


@app.route('/api/dashboard/top-products', methods=['GET'])
def get_top_products():
    limit = int(request.args.get('limit', 5))
    products = db.get_top_products(limit=limit)
    return jsonify(products)


@app.route('/api/dashboard/category-sales', methods=['GET'])
def get_category_sales():
    data = db.get_category_sales()
    return jsonify(data)


@app.route('/api/dashboard/inventory-logs', methods=['GET'])
def get_inventory_logs():
    limit = int(request.args.get('limit', 50))
    logs = db.get_inventory_logs(limit=limit)
    return jsonify(logs)


# ============== SETTINGS ENDPOINTS ==============

@app.route('/api/settings', methods=['GET'])
def get_settings():
    settings = db.get_all_settings()
    return jsonify(settings)


@app.route('/api/settings/<key>', methods=['PUT'])
def update_setting(key):
    data = request.get_json()
    success = db.update_setting(key, data.get('value', ''))
    return jsonify({'success': success})


# ============== HEALTH CHECK ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'POS API'})


# ============== SERVE REACT FRONTEND ==============

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve the React frontend for all non-API routes."""
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    # Check if the file exists in static folder
    file_path = os.path.join(STATIC_DIR, path)
    if path and os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(STATIC_DIR, path)
    
    # Serve index.html for all routes (SPA routing)
    return send_from_directory(STATIC_DIR, 'index.html')


if __name__ == '__main__':
    # Initialize database
    db.init_database()

    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
