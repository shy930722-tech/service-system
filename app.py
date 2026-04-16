from flask import Flask, request, redirect, render_template_string, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "123456"

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERNAME = "admin"
PASSWORD = "123456"

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
            service TEXT,
            note TEXT,
            document TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            service TEXT,
            income REAL,
            cost REAL,
            profit REAL,
            note TEXT
        )
    ''')

    conn.commit()
    conn.close()

login_html = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: Arial; background:#f5f7fb; display:flex; justify-content:center; align-items:center; height:100vh; }
.box { background:white; padding:30px; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,0.1); width:300px; text-align:center; }
input { width:90%; padding:10px; margin:10px 0; }
button { padding:10px 20px; background:#4f46e5; color:white; border:none; border-radius:5px; }
</style>
</head>
<body>
<div class="box">
<h2>后台登录</h2>
<form method="post">
<input name="username" placeholder="账号">
<input name="password" type="password" placeholder="密码">
<button type="submit">登录</button>
</form>
</div>
</body>
</html>
"""

dashboard_html = """
<!DOCTYPE html>
<html>
<head>
<title>业务后台</title>
<style>
body { font-family: Arial; background:#f5f7fb; padding:20px; margin:0; }
.header { display:flex; align-items:center; margin-bottom:20px; }
.logo { width:60px; height:60px; margin-right:15px; }
.cards { display:flex; gap:15px; margin-bottom:20px; }
.card { flex:1; background:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.08); font-weight:bold; }
form, table { background:white; padding:15px; margin-bottom:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.08); width:100%; }
input, select, button { padding:10px; margin:5px; }
table { border-collapse: collapse; }
th { background:#4f46e5; color:white; padding:10px; }
td { padding:10px; border-bottom:1px solid #eee; }
button { background:#4f46e5; color:white; border:none; border-radius:5px; }
a { color:red; text-decoration:none; }
</style>
</head>
<body>

<div class="header">
< img src="https://raw.githubusercontent.com/shy930722-tech/service-system/7ad49cca985aaa63757606db4c3b6a1643cf4d8f/logo.png" class="logo">
<h1>勇闯泰兰德业务后台</h1>
</div>

<div class="cards">
<div class="card">客户总数：{{ customer_count }}</div>
<div class="card">订单总数：{{ order_count }}</div>
<div class="card">总利润：{{ total_profit }}</div>
</div>

<h2>新增客户</h2>
<form method="post" action="/add_customer">
<input name="name" placeholder="客户姓名" required>
<input name="phone" placeholder="电话" required>
<select name="service">
{% for s in service_types %}
<option value="{{ s }}">{{ s }}</option>
{% endfor %}
</select>
<input name="note" placeholder="备注">
<input name="document" placeholder="证件图片链接">
<button type="submit">添加客户</button>
</form>

<h2>客户列表</h2>
<table>
<tr><th>姓名</th><th>电话</th><th>业务</th><th>备注</th><th>证件</th><th>操作</th></tr>
{% for c in customers %}
<tr>
<td>{{ c[1] }}</td>
<td>{{ c[2] }}</td>
<td>{{ c[3] }}</td>
<td>{{ c[4] }}</td>
<td>{% if c[5] %}<a href=" " target="_blank">查看</a >{% endif %}</td>
<td><a href="/delete_customer/{{ c[0] }}">删除</a ></td>
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
<input name="note" placeholder="业务备注">
<button type="submit">添加订单</button>
</form>

<h2>订单列表</h2>
<table>
<tr><th>客户</th><th>业务</th><th>收入</th><th>成本</th><th>利润</th><th>备注</th><th>操作</th></tr>
{% for o in orders %}
<tr>
<td>{{ o[1] }}</td>
<td>{{ o[2] }}</td>
<td>{{ o[3] }}</td>
<td>{{ o[4] }}</td>
<td>{{ o[5] }}</td>
<td>{{ o[6] }}</td>
<td><a href="/delete_order/{{ o[0] }}">删除</a ></td>
</tr>
{% endfor %}
</table>

<a href="/logout">退出登录</a >
</body>
</html>
"""

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['user'] = USERNAME
            return redirect('/')
    return render_template_string(login_html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')

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

    return render_template_string(dashboard_html,
        customers=customers,
        orders=orders,
        customer_count=customer_count,
        order_count=order_count,
        total_profit=total_profit,
        service_types=service_types)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO customers (name, phone, service, note, document) VALUES (?, ?, ?, ?, ?)",
              (request.form['name'], request.form['phone'], request.form['service'], request.form['note'], request.form['document']))
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
    c.execute("INSERT INTO orders (customer, service, income, cost, profit, note) VALUES (?, ?, ?, ?, ?, ?)",
              (request.form['customer'], request.form['service'], income, cost, profit, request.form['note']))
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
