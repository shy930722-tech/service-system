from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def db():
    return sqlite3.connect("data.db")

def init_db():
    conn = db()
    c = conn.cursor()

    # 客户预约找房
    c.execute('''CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        status TEXT
    )''')

    # 拟找房客户
    c.execute('''CREATE TABLE IF NOT EXISTS pending(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        status TEXT
    )''')

    # 房东信息
    c.execute('''CREATE TABLE IF NOT EXISTS landlords(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        apartment TEXT,
        address TEXT,
        base_price REAL,
        note TEXT
    )''')

    # 公寓信息
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

    # 车辆业务
    c.execute('''CREATE TABLE IF NOT EXISTS cars(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        wechat TEXT,
        car_type TEXT,
        profit REAL,
        note TEXT
    )''')

    # 签证业务
    c.execute('''CREATE TABLE IF NOT EXISTS visa(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        visa_type TEXT,
        progress TEXT,
        profit REAL
    )''')

    # 跑腿业务
    c.execute('''CREATE TABLE IF NOT EXISTS errands(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        task TEXT,
        profit REAL
    )''')

    c.execute("SELECT COUNT(*) FROM apartments")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO apartments(name,status) VALUES('公寓1','空置')")
        c.execute("INSERT INTO apartments(name,status) VALUES('公寓2','空置')")
        c.execute("INSERT INTO apartments(name,status) VALUES('公寓3','空置')")

    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    conn = db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM customers")
    total_customers = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM pending")
    pending_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM landlords")
    landlord_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM apartments WHERE status='已出租'")
    rented_count = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(profit),0) FROM customers")
    customer_profit = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(profit),0) FROM cars")
    car_profit = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(profit),0) FROM visa")
    visa_profit = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(profit),0) FROM errands")
    errands_profit = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(profit),0) FROM apartments")
    apartment_profit = c.fetchone()[0]

    total_profit = customer_profit + car_profit + visa_profit + errands_profit + apartment_profit

    conn.close()

    return render_template("dashboard.html",
                           total_customers=total_customers,
                           pending_count=pending_count,
                           landlord_count=landlord_count,
                           rented_count=rented_count,
                           total_profit=total_profit)

@app.route('/customers')
def customers():
    return render_table("customers", "customers.html")

@app.route('/pending')
def pending():
    return render_table("pending", "customers.html")

@app.route('/landlords')
def landlords():
    return render_table("landlords", "landlords.html")

@app.route('/cars')
def cars():
    return render_table("cars", "cars.html")

@app.route('/visa')
def visa():
    return render_table("visa", "visa.html")

@app.route('/errands')
def errands():
    return render_table("errands", "errands.html")

@app.route('/apartments')
def apartments():
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM apartments")
    data = c.fetchall()
    conn.close()
    return render_template("apartments.html", data=data)

@app.route('/finance')
def finance():
    conn = db()
    c = conn.cursor()

    tables = ["customers","cars","visa","errands","apartments"]
    profits = {}
    total = 0

    for t in tables:
        c.execute(f"SELECT COALESCE(SUM(profit),0) FROM {t}")
        p = c.fetchone()[0]
        profits[t] = p
        total += p

    conn.close()
    return render_template("finance.html", profits=profits, total=total)

def render_table(table, template):
    conn = db()
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table}")
    data = c.fetchall()
    conn.close()
    return render_template(template, data=data)

init_db()

if __name__ == "__main__":
    app.run()
