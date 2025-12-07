from flask import Flask, request, jsonify
import sqlite3
import os
import random
import string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DB_NAME = "products.db"


# -----------------------------
# Database connection helper
# -----------------------------
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row   # return rows as dict-like
    return conn


# -----------------------------
# Database initialization
# -----------------------------
def init_db():
    """Create DB + table + seed random data if DB did not exist."""
    first_time = not os.path.exists(DB_NAME)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    conn.commit()

    if first_time:
        seed_random_products(conn)

    conn.close()


def seed_random_products(conn):
    """Insert 5 random products on first run."""
    print("Seeding random products...")

    for _ in range(5):
        name = "Product_" + ''.join(random.choices(string.ascii_uppercase, k=5))
        price = round(random.uniform(10, 100), 2)

        conn.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))

    conn.commit()


# -----------------------------
# Routes
# -----------------------------
@app.route("/products", methods=["GET"])
def get_products():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()

    if not data or "name" not in data or "price" not in data:
        return jsonify({"error": "Missing 'name' or 'price'"}), 400

    conn = get_connection()

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        (data["name"], data["price"])
    )
    conn.commit()

    new_id = cur.lastrowid
    conn.close()

    return jsonify({"id": new_id, "message": "Product added"}), 201


# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=3000)
