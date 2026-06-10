"""
POS System Database Module
Handles all database operations for the Point of Sale system using SQLite.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'pos_database.db')


def get_db_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize the database with all tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            role TEXT NOT NULL DEFAULT 'cashier',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            sku TEXT UNIQUE NOT NULL,
            barcode TEXT UNIQUE,
            category_id INTEGER,
            price REAL NOT NULL,
            cost_price REAL DEFAULT 0,
            quantity INTEGER DEFAULT 0,
            min_stock_level INTEGER DEFAULT 10,
            unit TEXT DEFAULT 'piece',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            loyalty_points INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            user_id INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            tax_amount REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'cash',
            payment_status TEXT DEFAULT 'paid',
            status TEXT DEFAULT 'completed',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Order Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Inventory Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            previous_stock INTEGER NOT NULL,
            new_stock INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT
        )
    ''')

    conn.commit()

    # Insert default data
    seed_database(conn)

    conn.close()
    print("Database initialized successfully!")


def seed_database(conn):
    """Seed the database with default data."""
    cursor = conn.cursor()

    # Check if users already exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Default admin user
        cursor.execute('''
            INSERT INTO users (username, password, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin123', 'System Administrator', 'admin@pos.com', 'admin'))

        # Default cashier user
        cursor.execute('''
            INSERT INTO users (username, password, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('cashier', 'cashier123', 'Default Cashier', 'cashier@pos.com', 'cashier'))

    # Check if categories exist
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('Electronics', 'Electronic devices and accessories'),
            ('Groceries', 'Food items and beverages'),
            ('Clothing', 'Apparel and fashion items'),
            ('Home & Garden', 'Home improvement and gardening'),
            ('Sports', 'Sports equipment and accessories'),
            ('Books', 'Books and stationery'),
            ('Health & Beauty', 'Health and beauty products'),
            ('Toys', 'Toys and games')
        ]
        cursor.executemany('''
            INSERT INTO categories (name, description) VALUES (?, ?)
        ''', categories)

    # Check if products exist
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ('Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 'SKU-001', '1234567890123', 1, 29.99, 15.00, 50, 10, 'piece'),
            ('USB-C Cable', 'Fast charging USB-C cable 1.5m', 'SKU-002', '1234567890124', 1, 12.99, 5.00, 100, 20, 'piece'),
            ('Organic Apples', 'Fresh organic apples 1kg bag', 'SKU-003', '1234567890125', 2, 4.99, 2.50, 30, 15, 'kg'),
            ('Whole Milk', 'Fresh whole milk 1 liter', 'SKU-004', '1234567890126', 2, 3.49, 1.80, 40, 20, 'liter'),
            ('Cotton T-Shirt', 'Premium cotton t-shirt, various sizes', 'SKU-005', '1234567890127', 3, 19.99, 8.00, 60, 15, 'piece'),
            ('Denim Jeans', 'Classic fit denim jeans', 'SKU-006', '1234567890128', 3, 49.99, 25.00, 35, 10, 'piece'),
            ('LED Desk Lamp', 'Adjustable LED desk lamp with USB port', 'SKU-007', '1234567890129', 4, 34.99, 18.00, 25, 8, 'piece'),
            ('Yoga Mat', 'Non-slip exercise yoga mat', 'SKU-008', '1234567890130', 5, 24.99, 12.00, 40, 10, 'piece'),
            ('Basketball', 'Official size indoor/outdoor basketball', 'SKU-009', '1234567890131', 5, 29.99, 15.00, 20, 8, 'piece'),
            ('Novel - Bestseller', 'Popular fiction novel paperback', 'SKU-010', '1234567890132', 6, 14.99, 7.50, 45, 15, 'piece'),
            ('Notebook Set', 'Pack of 3 lined notebooks A5', 'SKU-011', '1234567890133', 6, 9.99, 4.50, 60, 20, 'set'),
            ('Face Cream', 'Moisturizing face cream 50ml', 'SKU-012', '1234567890134', 7, 18.99, 9.00, 30, 10, 'piece'),
            ('Shampoo', 'Natural herbal shampoo 400ml', 'SKU-013', '1234567890135', 7, 8.99, 4.50, 50, 15, 'piece'),
            ('Building Blocks', 'Creative building blocks set 100pcs', 'SKU-014', '1234567890136', 8, 34.99, 18.00, 25, 8, 'set'),
            ('Board Game', 'Family strategy board game', 'SKU-015', '1234567890137', 8, 39.99, 20.00, 15, 5, 'piece')
        ]
        cursor.executemany('''
            INSERT INTO products (name, description, sku, barcode, category_id, price, cost_price, quantity, min_stock_level, unit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', products)

    # Check if customers exist
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        customers = [
            ('John Smith', 'john.smith@email.com', '555-0101', '123 Main St', 'New York', 150),
            ('Sarah Johnson', 'sarah.j@email.com', '555-0102', '456 Oak Ave', 'Los Angeles', 230),
            ('Michael Brown', 'mbrown@email.com', '555-0103', '789 Pine Rd', 'Chicago', 75),
            ('Emily Davis', 'emily.d@email.com', '555-0104', '321 Elm St', 'Houston', 310),
            ('Robert Wilson', 'rwilson@email.com', '555-0105', '654 Maple Dr', 'Phoenix', 45)
        ]
        cursor.executemany('''
            INSERT INTO customers (name, email, phone, address, city, loyalty_points)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', customers)

    # Insert default settings
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        settings = [
            ('store_name', 'SuperMart POS', 'Store name displayed on receipts'),
            ('store_address', '123 Commerce Street, Business City', 'Store physical address'),
            ('store_phone', '555-0199', 'Store contact phone'),
            ('tax_rate', '8.5', 'Default tax rate percentage'),
            ('currency', 'USD', 'Currency code'),
            ('receipt_footer', 'Thank you for shopping with us!', 'Footer text on receipts'),
        ]
        cursor.executemany('''
            INSERT INTO settings (key, value, description) VALUES (?, ?, ?)
        ''', settings)

    conn.commit()


# ============== USER OPERATIONS ==============

def get_all_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_user_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_username(username):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_user(data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, full_name, email, phone, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['username'], data['password'], data['full_name'],
              data.get('email', ''), data.get('phone', ''), data.get('role', 'cashier')))
        return cursor.lastrowid


def update_user(user_id, data):
    with get_db() as conn:
        cursor = conn.cursor()
        fields = []
        values = []
        for key in ['username', 'password', 'full_name', 'email', 'phone', 'role', 'is_active']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        if not fields:
            return False
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
        return cursor.rowcount > 0


def delete_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0


# ============== CATEGORY OPERATIONS ==============

def get_all_categories():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]


def get_category_by_id(category_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_category(data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO categories (name, description) VALUES (?, ?)
        ''', (data['name'], data.get('description', '')))
        return cursor.lastrowid


def update_category(category_id, data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE categories SET name = ?, description = ? WHERE id = ?
        ''', (data['name'], data.get('description', ''), category_id))
        return cursor.rowcount > 0


def delete_category(category_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        return cursor.rowcount > 0


# ============== PRODUCT OPERATIONS ==============

def get_all_products(search=None, category_id=None, low_stock=False):
    with get_db() as conn:
        cursor = conn.cursor()
        query = '''
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE 1=1
        '''
        params = []
        if search:
            query += " AND (p.name LIKE ? OR p.sku LIKE ? OR p.barcode LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
        if low_stock:
            query += " AND p.quantity <= p.min_stock_level"
        query += " ORDER BY p.created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_product_by_id(product_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        ''', (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_product_by_barcode(barcode):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.barcode = ?
        ''', (barcode,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_product(data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, description, sku, barcode, category_id, price, cost_price, quantity, min_stock_level, unit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['name'], data.get('description', ''), data['sku'],
              data.get('barcode', ''), data.get('category_id'), data['price'],
              data.get('cost_price', 0), data.get('quantity', 0),
              data.get('min_stock_level', 10), data.get('unit', 'piece')))
        product_id = cursor.lastrowid
        # Log inventory
        if data.get('quantity', 0) > 0:
            cursor.execute('''
                INSERT INTO inventory_logs (product_id, type, quantity, previous_stock, new_stock, notes)
                VALUES (?, 'initial', ?, 0, ?, 'Initial stock')
            ''', (product_id, data['quantity'], data['quantity']))
        return product_id


def update_product(product_id, data):
    with get_db() as conn:
        cursor = conn.cursor()
        # Get current quantity
        cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return False
        prev_qty = row['quantity']

        fields = []
        values = []
        for key in ['name', 'description', 'sku', 'barcode', 'category_id', 'price',
                    'cost_price', 'quantity', 'min_stock_level', 'unit', 'is_active']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        if not fields:
            return False
        values.append(product_id)
        cursor.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = ?", values)

        # Log inventory change if quantity changed
        if 'quantity' in data and data['quantity'] != prev_qty:
            change = data['quantity'] - prev_qty
            cursor.execute('''
                INSERT INTO inventory_logs (product_id, type, quantity, previous_stock, new_stock, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (product_id, 'adjustment' if change > 0 else 'sale', abs(change),
                  prev_qty, data['quantity'], 'Manual adjustment'))

        return cursor.rowcount > 0


def delete_product(product_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return cursor.rowcount > 0


# ============== CUSTOMER OPERATIONS ==============

def get_all_customers(search=None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM customers WHERE 1=1"
        params = []
        if search:
            query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        query += " ORDER BY name"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_customer_by_id(customer_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_customer(data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (name, email, phone, address, city, loyalty_points)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['name'], data.get('email', ''), data.get('phone', ''),
              data.get('address', ''), data.get('city', ''), data.get('loyalty_points', 0)))
        return cursor.lastrowid


def update_customer(customer_id, data):
    with get_db() as conn:
        cursor = conn.cursor()
        fields = []
        values = []
        for key in ['name', 'email', 'phone', 'address', 'city', 'loyalty_points', 'is_active']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        if not fields:
            return False
        values.append(customer_id)
        cursor.execute(f"UPDATE customers SET {', '.join(fields)} WHERE id = ?", values)
        return cursor.rowcount > 0


def delete_customer(customer_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        return cursor.rowcount > 0


# ============== ORDER OPERATIONS ==============

def get_all_orders(limit=None, offset=0):
    with get_db() as conn:
        cursor = conn.cursor()
        query = '''
            SELECT o.*, c.name as customer_name, u.full_name as user_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
        '''
        params = []
        if limit:
            query += " LIMIT ? OFFSET ?"
            params = [limit, offset]
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_order_by_id(order_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*, c.name as customer_name, u.full_name as user_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN users u ON o.user_id = u.id
            WHERE o.id = ?
        ''', (order_id,))
        order = cursor.fetchone()
        if not order:
            return None
        order_dict = dict(order)

        # Get order items
        cursor.execute('''
            SELECT oi.*, p.name as product_name, p.sku
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        order_dict['items'] = [dict(row) for row in cursor.fetchall()]
        return order_dict


def create_order(data):
    with get_db() as conn:
        cursor = conn.cursor()

        # Generate order number
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0] + 1
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{count:04d}"

        # Insert order
        cursor.execute('''
            INSERT INTO orders (order_number, customer_id, user_id, subtotal, tax_amount, discount_amount, total_amount, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_number, data.get('customer_id'), data['user_id'],
              data['subtotal'], data.get('tax_amount', 0),
              data.get('discount_amount', 0), data['total_amount'],
              data.get('payment_method', 'cash'), data.get('notes', '')))
        order_id = cursor.lastrowid

        # Insert order items and update inventory
        for item in data['items']:
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, item['product_id'], item['quantity'],
                  item['unit_price'], item['total_price']))

            # Update product quantity
            cursor.execute("SELECT quantity FROM products WHERE id = ?", (item['product_id'],))
            prev_qty = cursor.fetchone()['quantity']
            new_qty = prev_qty - item['quantity']
            cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_qty, item['product_id']))

            # Log inventory
            cursor.execute('''
                INSERT INTO inventory_logs (product_id, type, quantity, previous_stock, new_stock, notes)
                VALUES (?, 'sale', ?, ?, ?, 'Order sale')
            ''', (item['product_id'], item['quantity'], prev_qty, new_qty))

        # Update customer loyalty points
        if data.get('customer_id'):
            points = int(data['total_amount'] / 10)
            cursor.execute('''
                UPDATE customers SET loyalty_points = loyalty_points + ? WHERE id = ?
            ''', (points, data['customer_id']))

        return order_id


def delete_order(order_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        return cursor.rowcount > 0


# ============== DASHBOARD & ANALYTICS ==============

def get_dashboard_stats():
    with get_db() as conn:
        cursor = conn.cursor()
        stats = {}

        # Total products
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE is_active = 1")
        stats['total_products'] = cursor.fetchone()['count']

        # Total customers
        cursor.execute("SELECT COUNT(*) as count FROM customers WHERE is_active = 1")
        stats['total_customers'] = cursor.fetchone()['count']

        # Total orders today
        cursor.execute('''
            SELECT COUNT(*) as count FROM orders
            WHERE DATE(created_at) = DATE('now')
        ''')
        stats['orders_today'] = cursor.fetchone()['count']

        # Total sales today
        cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0) as total FROM orders
            WHERE DATE(created_at) = DATE('now')
        ''')
        stats['sales_today'] = cursor.fetchone()['total']

        # Low stock products
        cursor.execute('''
            SELECT COUNT(*) as count FROM products
            WHERE quantity <= min_stock_level AND is_active = 1
        ''')
        stats['low_stock_count'] = cursor.fetchone()['count']

        # Total revenue
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as total FROM orders")
        stats['total_revenue'] = cursor.fetchone()['total']

        return stats


def get_sales_chart_data(period='week'):
    with get_db() as conn:
        cursor = conn.cursor()
        if period == 'week':
            cursor.execute('''
                SELECT date(created_at) as date, SUM(total_amount) as total, COUNT(*) as orders
                FROM orders
                WHERE created_at >= date('now', '-7 days')
                GROUP BY date(created_at)
                ORDER BY date
            ''')
        elif period == 'month':
            cursor.execute('''
                SELECT strftime('%Y-%m-%d', created_at) as date, SUM(total_amount) as total, COUNT(*) as orders
                FROM orders
                WHERE created_at >= date('now', '-30 days')
                GROUP BY strftime('%Y-%m-%d', created_at)
                ORDER BY date
            ''')
        elif period == 'year':
            cursor.execute('''
                SELECT strftime('%Y-%m', created_at) as date, SUM(total_amount) as total, COUNT(*) as orders
                FROM orders
                WHERE created_at >= date('now', '-12 months')
                GROUP BY strftime('%Y-%m', created_at)
                ORDER BY date
            ''')
        return [dict(row) for row in cursor.fetchall()]


def get_top_products(limit=5):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.name, SUM(oi.quantity) as total_sold, SUM(oi.total_price) as revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY oi.product_id
            ORDER BY total_sold DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]


def get_category_sales():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.name, SUM(oi.total_price) as revenue, COUNT(*) as sales_count
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            GROUP BY p.category_id
            ORDER BY revenue DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]


def get_inventory_logs(limit=50):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT il.*, p.name as product_name
            FROM inventory_logs il
            JOIN products p ON il.product_id = p.id
            ORDER BY il.created_at DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]


# ============== SETTINGS OPERATIONS ==============

def get_all_settings():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings")
        return [dict(row) for row in cursor.fetchall()]


def update_setting(key, value):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
        return cursor.rowcount > 0


if __name__ == '__main__':
    init_database()
