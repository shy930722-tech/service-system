from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

USERNAME = "admin"
PASSWORD = "admin123"

def db():
    return sqlite3.connect("data.db")

def init_db():
    conn = db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT,
        name TEXT,
        wechat TEXT,
        phone TEXT,
        checkin TEXT,
        room_type TEXT,
        duration TEXT,
        area TEXT,
        budget REAL,
        request TEXT,
        profit REAL,
        status TEXT,
        follow_up TEXT,
        follow_time TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS pending(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT,
        name TEXT,
        wechat TEXT,
        phone TEXT,
        checkin TEXT,
        room_type TEXT,
        duration TEXT,
        area TEXT,
        budget REAL,
        request TEXT,
        profit REAL,
        status TEXT,
        follow_up TEXT,
        follow_time TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS landlords(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        apartment TEXT,
        address TEXT,
        base_price REAL,
        note TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS apartments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        status TEXT,
        customer TEXT,
        rent REAL,
        cost REAL,
        profit REAL,
        checkin TEXT,
        checkout TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS cars(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        wechat TEXT,
        car_type TEXT,
        profit REAL,
        note TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS visa(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        visa_type TEXT,
        progress TEXT,
        profit REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS errands(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        task TEXT,
        profit REAL
    )''')

    c.execute("SELECT COUNT(*) FROM apartments")
    if c.fetchone()[0] == 0:
        for i in range(1,4):
            c.execute("INSERT INTO apartments(name,status) VALUES(?,?)", (f"公寓{i}", "空置"))

    conn.commit()
    conn.close()

def logged_in():
    return "user" in session

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session["user"] = USERNAME
            return redirect('/')
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def dashboard():
    if not logged_in():
        return redirect('/login')

    conn = db()
    c = conn.cursor()

    counts = {}
    for t in ["customers", "pending", "landlords"]:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        counts[t] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM apartments WHERE status='已出租'")
    rented_count = c.fetchone()[0]

    total_profit = 0
    for t in ["customers", "cars", "visa", "errands", "apartments"]:
        c.execute(f"SELECT COALESCE(SUM(profit),0) FROM {t}")
        total_profit += c.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           total_customers=counts["customers"],
                           pending_count=counts["pending"],
                           landlord_count=counts["landlords"],
                           rented_count=rented_count,
                           total_profit=total_profit)

@app.route('/customers')
def customers():
    if not logged_in():
        return redirect('/login')

    keyword = request.args.get("keyword","")
    conn = db()
    c = conn.cursor()

    if keyword:
        c.execute("SELECT * FROM customers WHERE name LIKE ? OR wechat LIKE ?", (f"%{keyword}%", f"%{keyword}%"))
    else:
        c.execute("SELECT * FROM customers")

    data = c.fetchall()
    conn.close()

    return render_template("customers.html", data=data, keyword=keyword)

@app.route('/apartments')
def apartments():
    if not logged_in():
        return redirect('/login')

    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM apartments")
    data = c.fetchall()
    conn.close()

    return render_template("apartments.html", data=data)

@app.route('/finance')
def finance():
    if not logged_in():
        return redirect('/login')

    conn = db()
    c = conn.cursor()

    profits = {}
    total = 0

    for t in ["customers","cars","visa","errands","apartments"]:
        c.execute(f"SELECT COALESCE(SUM(profit),0) FROM {t}")
        profits[t] = c.fetchone()[0]
        total += profits[t]

    conn.close()
    return render_template("finance.html", profits=profits, total=total)

init_db()

if __name__ == "__main__":
    app.run()
