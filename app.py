from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import time

app = Flask(__name__)

CATEGORIES = ["Fruits", "Vegetables", "Bakery"]

def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "db"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root123"),
        database=os.getenv("MYSQL_DATABASE", "grocerydb")
    )

def init_db():
    # Wait for MySQL to be ready
    for _ in range(10):
        try:
            conn = get_db()
            break
        except:
            time.sleep(3)

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category ENUM('Fruits', 'Vegetables', 'Bakery') NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            quantity INT NOT NULL,
            unit VARCHAR(20) NOT NULL,
            description VARCHAR(255)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.route("/")
def index():
    category = request.args.get("category", "All")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if category == "All":
        cursor.execute("SELECT * FROM products ORDER BY category, name")
    else:
        cursor.execute("SELECT * FROM products WHERE category = %s ORDER BY name", (category,))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", products=products, categories=CATEGORIES, selected=category)

@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, category, price, quantity, unit, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form["name"],
            request.form["category"],
            request.form["price"],
            request.form["quantity"],
            request.form["unit"],
            request.form["description"]
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html", categories=CATEGORIES)

@app.route("/delete/<int:product_id>")
def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        cursor.execute("""
            UPDATE products SET name=%s, category=%s, price=%s, quantity=%s, unit=%s, description=%s
            WHERE id=%s
        """, (
            request.form["name"],
            request.form["category"],
            request.form["price"],
            request.form["quantity"],
            request.form["unit"],
            request.form["description"],
            product_id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("index"))
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("edit.html", product=product, categories=CATEGORIES)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)