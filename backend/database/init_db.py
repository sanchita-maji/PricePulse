from database.db import get_connection


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT UNIQUE,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            category TEXT,
            rating REAL,
            availability TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            original_price REAL,
            discount_percentage REAL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discount_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            original_price REAL,
            sale_price REAL,
            discount_percentage REAL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()