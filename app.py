from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS customers(id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS pending(id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS apartments(id INTEGER PRIMARY KEY,status TEXT,profit REAL)")

    c.execute("SELECT COUNT(*) FROM customers")
    total_customers = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM pending")
    pending_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM apartments WHERE status='已出租'")
    rented_count = c.fetchone()[0]

    c.execute("SELECT SUM(profit) FROM apartments")
    total_profit = c.fetchone()[0] or 0

    conn.commit()
    conn.close()

    return render_template(
        "dashboard.html",
        total_customers=total_customers,
        pending_count=pending_count,
        rented_count=rented_count,
        total_profit=total_profit
    )

if __name__ == "__main__":
    app.run()
