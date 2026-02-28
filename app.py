import os
from flask import Flask, request, render_template, redirect, session, jsonify, g
import psycopg2
import hashlib
import yaml

app = Flask(__name__)

# VULNERABILITY: Hardcoded secret key
app.secret_key = "super_secret_key_12345_do_not_share"

# VULNERABILITY: Hardcoded database credentials
DB_HOST = "contoso-prod-db.postgres.database.azure.com"
DB_NAME = "contoso_store"
DB_USER = "admin_user"
DB_PASSWORD = "P@ssw0rd!2024_prod"
DB_PORT = "5432"

# VULNERABILITY: Hardcoded Stripe API key
STRIPE_SECRET_KEY = "stripe_live_key_rk7Xp2nQ9wLmT4vB8cYhJ1dF6gA3sK0eU5iO7zN"
STRIPE_PUBLISHABLE_KEY = "stripe_pub_key_aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5"


def get_db():
    """Get database connection"""
    if 'db' not in g:
        # VULNERABILITY: SSL disabled for database connection
        g.db = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode="disable"
        )
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = request.args.get('q', '')
    db = get_db()
    cursor = db.cursor()
    # VULNERABILITY: SQL Injection - user input directly in query
    sql = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
    cursor.execute(sql)
    products = cursor.fetchall()
    return render_template('search.html', products=products, query=query)


@app.route('/product/<product_id>')
def product_detail(product_id):
    db = get_db()
    cursor = db.cursor()
    # VULNERABILITY: SQL Injection
    cursor.execute(f"SELECT * FROM products WHERE id = {product_id}")
    product = cursor.fetchone()
    return render_template('product.html', product=product)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        # VULNERABILITY: SQL Injection in login
        sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(sql)
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[4]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # VULNERABILITY: MD5 for password hashing (weak)
        password_hash = hashlib.md5(password.encode()).hexdigest()

        db = get_db()
        cursor = db.cursor()
        # VULNERABILITY: SQL Injection
        cursor.execute(
            f"INSERT INTO users (username, email, password, is_admin) VALUES ('{username}', '{email}', '{password_hash}', false)"
        )
        db.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/admin')
def admin_panel():
    # VULNERABILITY: No authentication check for admin panel
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    return render_template('admin.html', users=users, orders=orders)


@app.route('/admin/export')
def admin_export():
    # VULNERABILITY: No auth check, exports all user data including passwords
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email, password, is_admin, created_at FROM users")
    users = cursor.fetchall()
    return jsonify([{
        'id': u[0], 'username': u[1], 'email': u[2],
        'password_hash': u[3], 'is_admin': u[4], 'created_at': str(u[5])
    } for u in users])


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    quantity = request.form['quantity']

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'product_id': product_id, 'quantity': quantity})
    session.modified = True
    return redirect('/cart')


@app.route('/checkout', methods=['POST'])
def checkout():
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY

    # VULNERABILITY: Price comes from client side, not recalculated server-side
    total = request.form.get('total')

    try:
        charge = stripe.Charge.create(
            amount=int(float(total) * 100),
            currency='usd',
            source=request.form['stripeToken'],
            description='Contoso Web Store Purchase'
        )
        return render_template('success.html', charge=charge)
    except stripe.error.CardError as e:
        return render_template('error.html', error=str(e))


@app.route('/api/config')
def api_config():
    """VULNERABILITY: Exposes internal configuration"""
    return jsonify({
        'database_host': DB_HOST,
        'database_name': DB_NAME,
        'database_user': DB_USER,
        'stripe_key': STRIPE_PUBLISHABLE_KEY,
        'debug_mode': True,
        'version': '1.0.0',
        'internal_api': 'https://internal-api.contoso.com/v1'
    })


@app.route('/api/webhook', methods=['POST'])
def webhook():
    # VULNERABILITY: No webhook signature verification
    data = request.get_json()
    if data.get('type') == 'payment_intent.succeeded':
        order_id = data['data']['object']['metadata']['order_id']
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f"UPDATE orders SET status = 'paid' WHERE id = {order_id}")
        db.commit()
    return jsonify({'status': 'ok'})


@app.route('/upload', methods=['POST'])
def upload_file():
    # VULNERABILITY: No file type validation
    file = request.files['file']
    file.save(os.path.join('/uploads', file.filename))
    return jsonify({'status': 'uploaded', 'filename': file.filename})


@app.route('/load-config', methods=['POST'])
def load_config():
    # VULNERABILITY: Unsafe YAML deserialization
    config_data = request.get_data()
    config = yaml.load(config_data, Loader=yaml.FullLoader)
    return jsonify({'status': 'loaded', 'keys': list(config.keys())})


if __name__ == '__main__':
    # VULNERABILITY: Debug mode enabled in production
    app.run(host='0.0.0.0', port=5000, debug=True)
