from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shopnest-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopnest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to continue.'

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), default='🛍️')
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500), default='')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Float, default=4.0)
    reviews_count = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    payment_method = db.Column(db.String(50), default='COD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_nav_categories():
    """Make categories available in ALL templates for navbar dropdown."""
    try:
        nav_cats = Category.query.all()
    except Exception:
        nav_cats = []
    return dict(nav_categories=nav_cats)

# ─────────────────────────────────────────────
# CART HELPERS
# ─────────────────────────────────────────────

def get_cart():
    return session.get('cart', {})

def get_cart_count():
    return sum(item['qty'] for item in get_cart().values())

def get_cart_total():
    return sum(item['price'] * item['qty'] for item in get_cart().values())

app.jinja_env.globals['get_cart_count'] = get_cart_count
app.jinja_env.globals['get_cart_total'] = get_cart_total

# ─────────────────────────────────────────────
# PUBLIC ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    featured = Product.query.filter_by(featured=True).limit(8).all()
    categories = Category.query.all()
    new_arrivals = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    total_products = Product.query.count()
    return render_template('index.html', featured=featured, categories=categories,
                           new_arrivals=new_arrivals, total_products=total_products)

@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('q', '')
    sort = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    return render_template('products.html', products=products, categories=categories,
                           current_category=category_id, search=search, sort=sort)

@app.route('/category/<int:id>')
def category_page(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('q', '')

    query = Product.query.filter_by(category_id=id)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    # Price range for this category
    all_in_cat = Product.query.filter_by(category_id=id)
    price_min = db.session.query(db.func.min(Product.price)).filter_by(category_id=id).scalar() or 0
    price_max = db.session.query(db.func.max(Product.price)).filter_by(category_id=id).scalar() or 999999
    return render_template('category.html', category=category, products=products,
                           categories=categories, sort=sort, search=search,
                           price_min=price_min, price_max=price_max,
                           min_price=min_price, max_price=max_price)

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    related = Product.query.filter_by(category_id=product.category_id).filter(Product.id != id).limit(4).all()
    return render_template('product_detail.html', product=product, related=related)

@app.route('/cart')
def cart():
    cart = get_cart()
    cart_items = []
    for pid, item in cart.items():
        product = Product.query.get(int(pid))
        if product:
            cart_items.append({'product': product, 'qty': item['qty'], 'subtotal': item['price'] * item['qty']})
    return render_template('cart.html', cart_items=cart_items)

@app.route('/cart/add/<int:id>', methods=['POST'])
def add_to_cart(id):
    product = Product.query.get_or_404(id)
    qty = int(request.form.get('qty', 1))
    cart = get_cart()
    pid = str(id)
    if pid in cart:
        cart[pid]['qty'] += qty
    else:
        cart[pid] = {'name': product.name, 'price': product.price, 'qty': qty, 'image': product.image_url}
    session['cart'] = cart
    flash(f'"{product.name}" added to your cart!', 'success')
    return redirect(request.referrer or url_for('products'))

@app.route('/cart/update/<int:id>', methods=['POST'])
def update_cart(id):
    qty = int(request.form.get('qty', 1))
    cart = get_cart()
    pid = str(id)
    if pid in cart:
        if qty <= 0:
            del cart[pid]
        else:
            cart[pid]['qty'] = qty
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:id>')
def remove_from_cart(id):
    cart = get_cart()
    pid = str(id)
    if pid in cart:
        del cart[pid]
    session['cart'] = cart
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('products'))
    if request.method == 'POST':
        address = request.form.get('address')
        phone = request.form.get('phone')
        payment = request.form.get('payment', 'COD')
        total = get_cart_total()
        order = Order(user_id=current_user.id, total=total, address=address,
                      phone=phone, payment_method=payment, status='Pending')
        db.session.add(order)
        db.session.flush()
        for pid, item in cart.items():
            oi = OrderItem(order_id=order.id, product_id=int(pid),
                           quantity=item['qty'], price=item['price'])
            db.session.add(oi)
            product = Product.query.get(int(pid))
            if product:
                product.stock = max(0, product.stock - item['qty'])
        db.session.commit()
        session['cart'] = {}
        flash(f'Order #{order.id} placed successfully! 🎉', 'success')
        return redirect(url_for('order_success', order_id=order.id))
    return render_template('checkout.html', total=get_cart_total())

@app.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_success.html', order=order)

@app.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}! 👋', 'success')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if password != confirm:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('This email is already registered!', 'danger')
            return render_template('register.html')
        user = User(name=name, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Account created! Welcome, {name}! 🎉', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# ─────────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'total_orders': Order.query.count(),
        'pending_orders': Order.query.filter_by(status='Pending').count(),
        'total_products': Product.query.count(),
        'total_users': User.query.filter_by(is_admin=False).count(),
        'total_revenue': db.session.query(db.func.sum(Order.total)).filter(Order.status != 'Cancelled').scalar() or 0,
        'delivered_orders': Order.query.filter_by(status='Delivered').count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    low_stock = Product.query.filter(Product.stock < 10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders, low_stock=low_stock)

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    cat_filter = request.args.get('cat', type=int)
    search = request.args.get('q', '')
    query = Product.query
    if cat_filter:
        query = query.filter_by(category_id=cat_filter)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    # product counts per category
    cat_counts = {}
    for c in categories:
        cat_counts[c.id] = Product.query.filter_by(category_id=c.id).count()
    return render_template('admin/products.html', products=products, categories=categories,
                           cat_filter=cat_filter, search=search, cat_counts=cat_counts)

@app.route('/admin/products/add', methods=['POST'])
@login_required
@admin_required
def admin_add_product():
    p = Product(
        name=request.form['name'],
        description=request.form['description'],
        price=float(request.form['price']),
        original_price=float(request.form['original_price']) if request.form.get('original_price') else None,
        stock=int(request.form['stock']),
        category_id=int(request.form['category_id']) if request.form.get('category_id') else None,
        featured=bool(request.form.get('featured')),
        image_url=request.form.get('image_url', ''),
        rating=float(request.form.get('rating', 4.0)),
    )
    db.session.add(p)
    db.session.commit()
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/products/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_edit_product(id):
    p = Product.query.get_or_404(id)
    p.name = request.form['name']
    p.description = request.form['description']
    p.price = float(request.form['price'])
    p.original_price = float(request.form['original_price']) if request.form.get('original_price') else None
    p.stock = int(request.form['stock'])
    p.category_id = int(request.form['category_id']) if request.form.get('category_id') else None
    p.featured = bool(request.form.get('featured'))
    p.image_url = request.form.get('image_url', p.image_url)
    p.rating = float(request.form.get('rating', p.rating))
    p.reviews_count = int(request.form.get('reviews_count', p.reviews_count or 0))
    db.session.commit()
    flash('Product updated successfully!', 'success')
    return redirect(url_for('admin_products', cat=request.form.get('cat_filter')))

@app.route('/admin/products/delete/<int:id>')
@login_required
@admin_required
def admin_delete_product(id):
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    status_filter = request.args.get('status', '')
    query = Order.query.order_by(Order.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.all()
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@app.route('/admin/orders/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_update_order(id):
    order = Order.query.get_or_404(id)
    order.status = request.form['status']
    db.session.commit()
    flash(f'Order #{id} status updated!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/toggle/<int:id>')
@login_required
@admin_required
def admin_toggle_user(id):
    user = User.query.get_or_404(id)
    if user.id != current_user.id:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash('User role updated successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_categories():
    if request.method == 'POST':
        c = Category(name=request.form['name'], icon=request.form.get('icon', '🛍️'))
        db.session.add(c)
        db.session.commit()
        flash('Category added successfully!', 'success')
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/delete/<int:id>')
@login_required
@admin_required
def admin_delete_category(id):
    c = Category.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_categories'))

# ─────────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────────

def seed_data():
    if Category.query.count() > 0:
        return
    categories = [
        Category(name='Electronics', icon='💻'),
        Category(name='Fashion', icon='👗'),
        Category(name='Home & Living', icon='🏠'),
        Category(name='Sports', icon='⚽'),
        Category(name='Beauty', icon='💄'),
        Category(name='Books', icon='📚'),
    ]
    db.session.add_all(categories)
    db.session.flush()

    products = [
        Product(name='iPhone 15 Pro Max', description='Latest Apple flagship with titanium design and 48MP camera system.', price=134900, original_price=149900, stock=25, category_id=1, featured=True, rating=4.8, reviews_count=2341, image_url='https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&q=80'),
        Product(name='Samsung Galaxy S24 Ultra', description='AI-powered smartphone with S Pen and 200MP camera.', price=124999, original_price=139999, stock=30, category_id=1, featured=True, rating=4.7, reviews_count=1876, image_url='https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&q=80'),
        Product(name='Sony WH-1000XM5 Headphones', description='Industry-leading noise canceling with 30hr battery life.', price=24990, original_price=34990, stock=50, category_id=1, featured=True, rating=4.9, reviews_count=4521, image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80'),
        Product(name='MacBook Air M3', description='Supercharged by M3 chip. Fanless design, all-day battery.', price=114900, original_price=124900, stock=15, category_id=1, featured=True, rating=4.9, reviews_count=987, image_url='https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80'),
        Product(name='Men\'s Premium Jacket', description='Stylish winter jacket with thermal lining. Perfect for cold weather.', price=3499, original_price=5999, stock=80, category_id=2, featured=True, rating=4.5, reviews_count=342, image_url='https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400&q=80'),
        Product(name='Women\'s Floral Dress', description='Elegant summer dress with floral print. Available in 5 sizes.', price=1299, original_price=2499, stock=120, category_id=2, featured=True, rating=4.6, reviews_count=567, image_url='https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400&q=80'),
        Product(name='Nike Air Max 270', description='Maximum comfort running shoes with large Air unit.', price=9999, original_price=13000, stock=45, category_id=4, featured=True, rating=4.7, reviews_count=1234, image_url='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80'),
        Product(name='Smart LED TV 55"', description='4K Ultra HD Smart TV with Dolby Vision and HDR10+.', price=42999, original_price=59999, stock=20, category_id=1, featured=True, rating=4.6, reviews_count=876, image_url='https://images.unsplash.com/photo-1593784991095-a205069470b6?w=400&q=80'),
        Product(name='Luxury Perfume Set', description='Exclusive French fragrance collection. Gift box included.', price=2499, original_price=3999, stock=60, category_id=5, featured=False, rating=4.8, reviews_count=453, image_url='https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=400&q=80'),
        Product(name='Yoga Mat Premium', description='Non-slip exercise mat with alignment lines. Eco-friendly material.', price=1299, original_price=1999, stock=90, category_id=4, featured=False, rating=4.5, reviews_count=678, image_url='https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&q=80'),
        Product(name='Coffee Table Modern', description='Minimalist design coffee table with tempered glass top.', price=8999, original_price=12999, stock=10, category_id=3, featured=False, rating=4.4, reviews_count=234, image_url='https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80'),
        Product(name='Bestseller Book Bundle', description='Top 5 motivational books to transform your mindset.', price=999, original_price=1799, stock=200, category_id=6, featured=False, rating=4.7, reviews_count=1567, image_url='https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&q=80'),
    ]
    db.session.add_all(products)

    admin = User(name='Admin', email='admin@shopnest.com',
                 password=generate_password_hash('admin123'), is_admin=True)
    db.session.add(admin)
    db.session.commit()
    print("✅ Sample data seeded!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
