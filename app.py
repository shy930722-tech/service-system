from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

USERNAME = "admin"
PASSWORD = "admin123"

MODULES = [
    "property_orders",
    "property_pending",
    "landlords",
    "apartments",
    "car_orders",
    "license_orders",
    "visa_orders",
    "errand_orders",
    "shopping_orders",
    "logistics_orders"
]

def db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    c = conn.cursor()

    for table in MODULES:
        c.execute(f'''
        CREATE TABLE IF NOT EXISTS {table}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            contact TEXT,
            service TEXT,
            status TEXT,
            profit REAL,
            note TEXT
        )
        ''')

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
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def dashboard():
    if not login_required():
        return redirect('/login')

    conn = db()
    total_orders = 0
    total_profit = 0

    stats = {}

    for table in MODULES:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        profit = conn.execute(f"SELECT COALESCE(SUM(profit),0) FROM {table}").fetchone()[0]
        stats[table] = count
        total_orders += count
        total_profit += profit

    conn.close()

    return render_template('dashboard.html',
                           stats=stats,
                           total_orders=total_orders,
                           total_profit=total_profit)

@app.route('/module/<table>', methods=['GET','POST'])
def module(table):
    if not login_required():
        return redirect('/login')

    if table not in MODULES:
        return "模块不存在"

    conn = db()

    if request.method == 'POST':
        conn.execute(f'''
        INSERT INTO {table}(customer,contact,service,status,profit,note)
        VALUES (?,?,?,?,?,?)
        ''',
        (
            request.form['customer'],
            request.form['contact'],
            request.form['service'],
            request.form['status'],
            request.form['profit'],
            request.form['note']
        ))
        conn.commit()

    data = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC").fetchall()
    conn.close()

    return render_template('module.html', data=data, table=table)

@app.route('/delete/<table>/<int:id>')
def delete(table,id):
    if table not in MODULES:
        return "模块不存在"

    conn = db()
    conn.execute(f"DELETE FROM {table} WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(f'/module/{table}')

init_db()

if __name__ == "__main__":
    app.run()
