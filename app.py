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
        name TEXT,wechat TEXT,phone TEXT,checkin TEXT,room_type TEXT,duration TEXT,
        area TEXT,budget REAL,request TEXT,profit REAL,status TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS landlords(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,contact TEXT,apartment TEXT,address TEXT,price REAL,note TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS cars(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,wechat TEXT,car_model TEXT,plan TEXT,profit REAL,note TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS visa(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,visa_type TEXT,progress TEXT,profit REAL,note TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS errands(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,task TEXT,profit REAL,status TEXT,note TEXT)''')

    conn.commit()
    conn.close()

def check_login():
    return "user" in session

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username']==USERNAME and request.form['password']==PASSWORD:
            session['user']="admin"
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def dashboard():
    if not check_login():
        return redirect('/login')

    conn = db()
    customer_count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    landlord_count = conn.execute("SELECT COUNT(*) FROM landlords").fetchone()[0]
    car_count = conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
    visa_count = conn.execute("SELECT COUNT(*) FROM visa").fetchone()[0]
    errand_count = conn.execute("SELECT COUNT(*) FROM errands").fetchone()[0]

    total_profit = 0
    total_profit += conn.execute("SELECT COALESCE(SUM(profit),0) FROM customers").fetchone()[0]
    total_profit += conn.execute("SELECT COALESCE(SUM(profit),0) FROM cars").fetchone()[0]
    total_profit += conn.execute("SELECT COALESCE(SUM(profit),0) FROM visa").fetchone()[0]
    total_profit += conn.execute("SELECT COALESCE(SUM(profit),0) FROM errands").fetchone()[0]

    conn.close()

    return render_template('dashboard.html',
                           customer_count=customer_count,
                           landlord_count=landlord_count,
                           car_count=car_count,
                           visa_count=visa_count,
                           errand_count=errand_count,
                           total_profit=total_profit)

@app.route('/customers', methods=['GET','POST'])
def customers():
    conn = db()
    if request.method == 'POST':
        conn.execute('''INSERT INTO customers(name,wechat,phone,checkin,room_type,duration,area,budget,request,profit,status)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
        (request.form['name'],request.form['wechat'],request.form['phone'],request.form['checkin'],
         request.form['room_type'],request.form['duration'],request.form['area'],request.form['budget'],
         request.form['request'],request.form['profit'],request.form['status']))
        conn.commit()
    data = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('customers.html', data=data)

@app.route('/landlords', methods=['GET','POST'])
def landlords():
    conn = db()
    if request.method == 'POST':
        conn.execute("INSERT INTO landlords(name,contact,apartment,address,price,note) VALUES(?,?,?,?,?,?)",
                     (request.form['name'],request.form['contact'],request.form['apartment'],
                      request.form['address'],request.form['price'],request.form['note']))
        conn.commit()
    data = conn.execute("SELECT * FROM landlords ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('landlords.html', data=data)

@app.route('/cars', methods=['GET','POST'])
def cars():
    conn = db()
    if request.method == 'POST':
        conn.execute("INSERT INTO cars(name,wechat,car_model,plan,profit,note) VALUES(?,?,?,?,?,?)",
                     (request.form['name'],request.form['wechat'],request.form['car_model'],
                      request.form['plan'],request.form['profit'],request.form['note']))
        conn.commit()
    data = conn.execute("SELECT * FROM cars ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('cars.html', data=data)

@app.route('/visa', methods=['GET','POST'])
def visa():
    conn = db()
    if request.method == 'POST':
        conn.execute("INSERT INTO visa(name,visa_type,progress,profit,note) VALUES(?,?,?,?,?)",
                     (request.form['name'],request.form['visa_type'],request.form['progress'],
                      request.form['profit'],request.form['note']))
        conn.commit()
    data = conn.execute("SELECT * FROM visa ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('visa.html', data=data)

@app.route('/errands', methods=['GET','POST'])
def errands():
    conn = db()
    if request.method == 'POST':
        conn.execute("INSERT INTO errands(name,task,profit,status,note) VALUES(?,?,?,?,?)",
                     (request.form['name'],request.form['task'],request.form['profit'],
                      request.form['status'],request.form['note']))
        conn.commit()
    data = conn.execute("SELECT * FROM errands ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('errands.html', data=data)

init_db()

if __name__ == "__main__":
    app.run()
