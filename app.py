from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

USERNAME = "admin"
PASSWORD = "admin123"

def db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        wechat TEXT,
        phone TEXT,
        checkin TEXT,
        room_type TEXT,
        budget REAL,
        status TEXT,
        follow_up TEXT,
        profit REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS landlords(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        apartment TEXT,
        rent REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS apartments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        status TEXT,
        tenant TEXT,
        rent REAL,
        cost REAL,
        profit REAL,
        checkout TEXT
    )''')

    c.execute("SELECT COUNT(*) FROM apartments")
    if c.fetchone()[0] == 0:
        for i in range(1,4):
            c.execute("INSERT INTO apartments(name,status) VALUES(?,?)",(f"公寓{i}","空置"))

    conn.commit()
    conn.close()

def login_required():
    return "user" in session

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['user'] = USERNAME
            return redirect('/')
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def dashboard():
    if not login_required():
        return redirect('/login')

    conn = db()
    customer_count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    rented_count = conn.execute("SELECT COUNT(*) FROM apartments WHERE status='已出租'").fetchone()[0]
    total_profit = conn.execute("SELECT COALESCE(SUM(profit),0) FROM customers").fetchone()[0]
    total_profit += conn.execute("SELECT COALESCE(SUM(profit),0) FROM apartments").fetchone()[0]
    conn.close()

    return render_template("dashboard.html",
                           customer_count=customer_count,
                           rented_count=rented_count,
                           total_profit=total_profit)

@app.route('/customers', methods=['GET','POST'])
def customers():
    if not login_required():
        return redirect('/login')

    conn = db()

    if request.method == 'POST':
        conn.execute('''INSERT INTO customers
        (name,wechat,phone,checkin,room_type,budget,status,follow_up,profit)
        VALUES (?,?,?,?,?,?,?,?,?)''',
        (
            request.form['name'],
            request.form['wechat'],
            request.form['phone'],
            request.form['checkin'],
            request.form['room_type'],
            request.form['budget'],
            request.form['status'],
            request.form['follow_up'],
            request.form['profit']
        ))
        conn.commit()

    keyword = request.args.get("keyword","")
    if keyword:
        data = conn.execute("SELECT * FROM customers WHERE name LIKE ?",('%'+keyword+'%',)).fetchall()
    else:
        data = conn.execute("SELECT * FROM customers").fetchall()

    conn.close()
    return render_template("customers.html", data=data)

@app.route('/delete_customer/<int:id>')
def delete_customer(id):
    conn = db()
    conn.execute("DELETE FROM customers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/customers')

@app.route('/apartments', methods=['GET','POST'])
def apartments():
    if not login_required():
        return redirect('/login')

    conn = db()

    if request.method == 'POST':
        conn.execute('''UPDATE apartments
        SET status=?,tenant=?,rent=?,cost=?,profit=?,checkout=?
        WHERE id=?''',
        (
            request.form['status'],
            request.form['tenant'],
            request.form['rent'],
            request.form['cost'],
            request.form['profit'],
            request.form['checkout'],
            request.form['id']
        ))
        conn.commit()

    data = conn.execute("SELECT * FROM apartments").fetchall()
    conn.close()

    return render_template("apartments.html", data=data)

@app.route('/landlords', methods=['GET','POST'])
def landlords():
    if request.method == 'POST':
        conn = db()
        conn.execute("INSERT INTO landlords(name,contact,apartment,rent) VALUES(?,?,?,?)",
                     (
                         request.form['name'],
                         request.form['contact'],
                         request.form['apartment'],
                         request.form['rent']
                     ))
        conn.commit()
        conn.close()

    conn = db()
    data = conn.execute("SELECT * FROM landlords").fetchall()
    conn.close()

    return render_template("landlords.html", data=data)

@app.route('/finance')
def finance():
    conn = db()
    customer_profit = conn.execute("SELECT COALESCE(SUM(profit),0) FROM customers").fetchone()[0]
    apartment_profit = conn.execute("SELECT COALESCE(SUM(profit),0) FROM apartments").fetchone()[0]
    total = customer_profit + apartment_profit
    conn.close()

    return render_template("finance.html",
                           customer_profit=customer_profit,
                           apartment_profit=apartment_profit,
                           total=total)

init_db()

if __name__ == "__main__":
    app.run()
