from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

service_types = [
    "租房服务",
    "买车服务",
    "驾照服务",
    "签证服务",
    "跑腿服务",
    "物流服务",
    "接机服务",
    "其他服务"
]

def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            service TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            service TEXT,
            income REAL,
            cost REAL,
            profit REAL
        )
    ''')

    conn.commit()
    conn.close()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>勇闯泰兰德业务后台</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        input, select, button { margin: 5px; padding: 8px; }
        table { border-collapse: collapse; width: 100%; margin-top: 15px; }
        table, th, td { border: 1px solid #ccc; padding: 8px; }
        .card { background: #f4f4f4; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>勇闯泰兰德业务后台</h1>

    <div class="card">客户总数：{{ customer_count }}</div>
    <div class="card">订单总数：{{ order_count }}</div>
    <div class="card">总利润：{{ total_profit }}</div>

    <h2>新增客户</h2>
    <form method="post" action="/add_customer">
        <input name="name" placeholder="客户姓名" required>
        <input name="phone" placeholder="电话" required>
        <select name="service">
            {% for s in service_types %}
            <option value="{{ s }}">{{ s }}</option>
            {% endfor %}
        </select>
        <button type="submit">添加客户</button>
    </form>

    <h2>客户列表</h2>
    <table>
        <tr><th>姓名</th><th>电话</th><th>业务</th><th>操作</th></tr>
        {% for c in customers %}
        <tr>
            <td>{{ c[1] }}</td>
            <td>{{ c[2] }}</td>
            <td>{{ c[3] }}</td>
            <td><a href=" ">删除</a ></td>
        </tr>
        {% endfor %}
    </table>

    <h2>新增订单</h2>
    <form method="post" action="/add_order">
        <input name="customer" placeholder="客户姓名" required>
        <select name="service">
            {% for s in service_types %}
            <option value="{{ s }}">{{ s }}</option>
            {% endfor %}
        </select>
        <input name="income" placeholder="收入" required>
        <input name="cost" placeholder="成本" required>
        <button type="submit">添加订单</button>
    </form>

    <h2>订单列表</h2>
    <table>
        <tr><th>客户</th><th>业务</th><th>收入</th><th>成本</th><th>利润</th><th>操作</th></tr>
        {% for o in orders %}
        <tr>
            <td>{{ o[1] }}</td>
            <td>{{ o[2] }}</td>
            <td>{{ o[3] }}</td>
            <td>{{ o[4] }}</td>
            <td>{{ o[5] }}</td>
            <td><a href="/delete_order/{{ o[0] }}">删除</a ></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def home():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("SELECT * FROM customers")
    customers = c.fetchall()

    c.execute("SELECT * FROM orders")
    orders = c.fetchall()

    c.execute("SELECT COUNT(*) FROM customers")
    customer_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM orders")
    order_count = c.fetchone()[0]

    c.execute("SELECT SUM(profit) FROM orders")
    total_profit = c.fetchone()[0] or 0

    conn.close()

    return render_template_string(
        html,
        customers=customers,
        orders=orders,
        customer_count=customer_count,
        order_count=order_count,
        total_profit=total_profit,
        service_types=service_types
    )

@app.route('/add_customer', methods=['POST'])
def add_customer():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO customers (name, phone, service) VALUES (?, ?, ?)",
        (request.form['name'], request.form['phone'], request.form['service'])
    )
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete_customer/<int:id>')
def delete_customer(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM customers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/add_order', methods=['POST'])
def add_order():
    income = float(request.form['income'])
    cost = float(request.form['cost'])
    profit = income - cost

    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (customer, service, income, cost, profit) VALUES (?, ?, ?, ?, ?)",
        (request.form['customer'], request.form['service'], income, cost, profit)
    )
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete_order/<int:id>')
def delete_order(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

init_db()

if __name__ == "__main__":
    app.run()
