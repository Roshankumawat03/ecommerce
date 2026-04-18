from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'shopx_secret_key_2024'
DATABASE = 'ecommerce.db'

# ─── DB HELPERS ───────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        original_price REAL,
        category TEXT,
        image_url TEXT,
        stock INTEGER DEFAULT 100,
        rating REAL DEFAULT 4.5,
        reviews INTEGER DEFAULT 0,
        badge TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total REAL,
        status TEXT DEFAULT 'Processing',
        address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')

    # Seed products if empty
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = [
            ("Apple iPhone 15 Pro", "Latest iPhone with titanium design, A17 Pro chip, and advanced camera system with 48MP main sensor.", 129999, 149999, "Electronics", "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&q=80", 50, 4.8, 2341, "New"),
            ("Samsung Galaxy S24 Ultra", "200MP camera, S Pen included, Snapdragon 8 Gen 3, 5000mAh battery.", 124999, 139999, "Electronics", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&q=80", 40, 4.7, 1892, "Hot"),
            ("Sony WH-1000XM5", "Industry-leading noise cancellation with 30-hour battery life and crystal clear hands-free calling.", 29999, 34999, "Audio", "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&q=80", 120, 4.9, 3210, "Bestseller"),
            ("MacBook Air M3", "Supercharged by M3 chip. 15.3‑inch Liquid Retina display. Up to 18 hours battery life.", 114900, 129900, "Laptops", "https://images.unsplash.com/photo-1611186871525-9f7a7da8f297?w=400&q=80", 30, 4.9, 1456, "New"),
            ("Nike Air Jordan 1 Retro", "Classic basketball shoe with premium leather upper. Iconic design in heritage colorway.", 12995, 15995, "Footwear", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80", 200, 4.6, 5678, "Sale"),
            ("Levi's 512 Slim Taper Jeans", "Slim through the hip and thigh with a tapered leg. Made with stretch fabric for comfort.", 3499, 4999, "Fashion", "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&q=80", 300, 4.4, 2109, None),
            ("Canon EOS R6 Mark II", "Full-frame mirrorless camera with 40fps burst shooting and in-body image stabilization.", 214995, 239995, "Cameras", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&q=80", 20, 4.8, 876, "New"),
            ("Dyson V15 Detect", "Laser dust detection, powerful suction, HEPA filtration. The most intelligent cordless vacuum.", 52900, 62900, "Home", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80", 60, 4.7, 1234, "Hot"),
            ("iPad Pro 12.9\" M2", "The ultimate iPad experience with M2 chip, Liquid Retina XDR display, and Apple Pencil support.", 109900, 119900, "Electronics", "https://images.unsplash.com/photo-1544244015-0df4cec9d125?w=400&q=80", 45, 4.8, 987, None),
            ("Adidas Ultraboost 23", "Boost cushioning technology for incredible energy return. Primeknit upper for adaptive fit.", 16999, 19999, "Footwear", "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&q=80", 150, 4.5, 3421, "Sale"),
            ("Bose QuietComfort 45", "Acclaimed noise cancellation, high-fidelity audio, comfortable design. 24-hour battery life.", 24999, 29999, "Audio", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80", 80, 4.6, 2876, None),
            ("LG OLED 55\" 4K TV", "OLED evo panel, α9 AI Processor 4K, Dolby Vision IQ & Dolby Atmos, 120Hz refresh rate.", 119990, 149990, "Electronics", "https://images.unsplash.com/photo-1593359677879-a4bb92f829e1?w=400&q=80", 25, 4.7, 765, "Sale"),
        ]
        c.executemany('''INSERT INTO products (name, description, price, original_price, category, image_url, stock, rating, reviews, badge)
                         VALUES (?,?,?,?,?,?,?,?,?,?)''', products)

    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── ROUTES ────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', '')

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR category LIKE ?)"
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    if category:
        query += " AND category = ?"
        params.append(category)
    if sort == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort == 'rating':
        query += " ORDER BY rating DESC"
    elif sort == 'newest':
        query += " ORDER BY id DESC"

    products = conn.execute(query, params).fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    featured = conn.execute("SELECT * FROM products WHERE badge IS NOT NULL LIMIT 4").fetchall()

    cart_count = 0
    if 'user_id' in session:
        row = conn.execute("SELECT SUM(quantity) FROM cart WHERE user_id=?", (session['user_id'],)).fetchone()
        cart_count = row[0] or 0

    conn.close()
    return render_template('index.html', products=products, categories=categories,
                           featured=featured, cart_count=cart_count,
                           search=search, category=category, sort=sort)

@app.route('/product/<int:pid>')
def product_detail(pid):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    related = conn.execute("SELECT * FROM products WHERE category=? AND id!=? LIMIT 4",
                           (product['category'], pid)).fetchall()
    cart_count = 0
    if 'user_id' in session:
        row = conn.execute("SELECT SUM(quantity) FROM cart WHERE user_id=?", (session['user_id'],)).fetchone()
        cart_count = row[0] or 0
    conn.close()
    return render_template('product_detail.html', product=product, related=related, cart_count=cart_count)

@app.route('/cart')
@login_required
def cart():
    conn = get_db()
    items = conn.execute('''
        SELECT c.id, c.quantity, p.id as pid, p.name, p.price, p.image_url, p.stock
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()
    subtotal = sum(i['price'] * i['quantity'] for i in items)
    cart_count = sum(i['quantity'] for i in items)
    conn.close()
    return render_template('cart.html', items=items, subtotal=subtotal, cart_count=cart_count)

@app.route('/add_to_cart/<int:pid>', methods=['POST'])
@login_required
def add_to_cart(pid):
    qty = int(request.form.get('quantity', 1))
    conn = get_db()
    existing = conn.execute("SELECT * FROM cart WHERE user_id=? AND product_id=?",
                            (session['user_id'], pid)).fetchone()
    if existing:
        conn.execute("UPDATE cart SET quantity=quantity+? WHERE id=?", (qty, existing['id']))
    else:
        conn.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?,?,?)",
                     (session['user_id'], pid, qty))
    conn.commit()
    conn.close()
    flash('Item added to cart!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/update_cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    qty = int(request.form.get('quantity', 1))
    conn = get_db()
    if qty <= 0:
        conn.execute("DELETE FROM cart WHERE id=? AND user_id=?", (cart_id, session['user_id']))
    else:
        conn.execute("UPDATE cart SET quantity=? WHERE id=? AND user_id=?",
                     (qty, cart_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    conn = get_db()
    conn.execute("DELETE FROM cart WHERE id=? AND user_id=?", (cart_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Item removed from cart', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    conn = get_db()
    items = conn.execute('''
        SELECT c.id, c.quantity, p.id as pid, p.name, p.price, p.image_url
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()

    if not items:
        flash('Your cart is empty!', 'warning')
        conn.close()
        return redirect(url_for('cart'))

    subtotal = sum(i['price'] * i['quantity'] for i in items)
    shipping = 99 if subtotal < 499 else 0
    total = subtotal + shipping
    cart_count = sum(i['quantity'] for i in items)

    if request.method == 'POST':
        address = f"{request.form['address']}, {request.form['city']}, {request.form['state']} - {request.form['pincode']}"
        order = conn.execute(
            "INSERT INTO orders (user_id, total, address, status) VALUES (?,?,?,?)",
            (session['user_id'], total, address, 'Confirmed')
        )
        order_id = order.lastrowid
        for item in items:
            conn.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?,?,?,?)",
                         (order_id, item['pid'], item['quantity'], item['price']))
        conn.execute("DELETE FROM cart WHERE user_id=?", (session['user_id'],))
        conn.commit()
        conn.close()
        flash(f'Order #{order_id} placed successfully! 🎉', 'success')
        return redirect(url_for('orders'))

    conn.close()
    return render_template('checkout.html', items=items, subtotal=subtotal,
                           shipping=shipping, total=total, cart_count=cart_count)

@app.route('/orders')
@login_required
def orders():
    conn = get_db()
    user_orders = conn.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",
        (session['user_id'],)
    ).fetchall()
    order_items_map = {}
    for o in user_orders:
        oi = conn.execute('''
            SELECT oi.*, p.name, p.image_url FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (o['id'],)).fetchall()
        order_items_map[o['id']] = oi
    cart_count = 0
    row = conn.execute("SELECT SUM(quantity) FROM cart WHERE user_id=?", (session['user_id'],)).fetchone()
    cart_count = row[0] or 0
    conn.close()
    return render_template('orders.html', orders=user_orders, order_items=order_items_map, cart_count=cart_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f'Welcome back, {user["name"]}! 👋', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        try:
            conn = get_db()
            conn.execute("INSERT INTO users (name, email, password) VALUES (?,?,?)", (name, email, password))
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            conn.close()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f'Welcome to ShopX, {name}! 🎉', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Email already registered', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/api/cart_count')
def cart_count_api():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    conn = get_db()
    row = conn.execute("SELECT SUM(quantity) FROM cart WHERE user_id=?", (session['user_id'],)).fetchone()
    conn.close()
    return jsonify({'count': row[0] or 0})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
