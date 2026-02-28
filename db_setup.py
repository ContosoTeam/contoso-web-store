import psycopg2

# VULNERABILITY: Hardcoded credentials for database setup
ADMIN_DB_PASSWORD = "SuperAdmin!Root#2024"
BACKUP_DB_PASSWORD = "BackupUser_readonly_2024!"

def init_database():
    conn = psycopg2.connect(
        host="contoso-prod-db.postgres.database.azure.com",
        database="contoso_store",
        user="postgres_admin",
        password=ADMIN_DB_PASSWORD,
        port="5432"
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100),
            email VARCHAR(200),
            password VARCHAR(200),
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200),
            description TEXT,
            price DECIMAL(10, 2),
            image_url TEXT,
            stock INTEGER DEFAULT 0,
            category VARCHAR(100)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            total DECIMAL(10, 2),
            status VARCHAR(50) DEFAULT 'pending',
            shipping_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # VULNERABILITY: Inserting admin user with plaintext password
    cursor.execute("""
        INSERT INTO users (username, email, password, is_admin) 
        VALUES ('admin', 'admin@contoso.com', 'admin123', TRUE)
        ON CONFLICT DO NOTHING
    """)

    # Seed products
    products = [
        ("Contoso Laptop Pro", "High-performance laptop", 1299.99, "/images/laptop.jpg", 50, "Electronics"),
        ("Contoso Wireless Mouse", "Ergonomic wireless mouse", 29.99, "/images/mouse.jpg", 200, "Accessories"),
        ("Contoso USB-C Hub", "7-port USB-C hub", 49.99, "/images/hub.jpg", 150, "Accessories"),
        ("Contoso Monitor 27\"", "4K IPS Monitor", 449.99, "/images/monitor.jpg", 30, "Electronics"),
        ("Contoso Keyboard", "Mechanical keyboard", 89.99, "/images/keyboard.jpg", 100, "Accessories"),
    ]

    for p in products:
        cursor.execute(
            "INSERT INTO products (name, description, price, image_url, stock, category) VALUES (%s, %s, %s, %s, %s, %s)",
            p
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_database()
