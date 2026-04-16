from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

customers = []
orders = []

html = """
<!DOCTYPE html>
<html>
<head>
    <title>业务后台</title>
</head>
<body>
    <h1>勇闯泰兰德业务后台</h1>

    <h2>添加客户</h2>
    <form method="post" action="/add_customer">
        姓名: <input name="name">
        业务: <input name="service">
        <button type="submit">添加</button>
    </form>

    <h2>客户列表</h2>
    <ul>
    {% for c in customers %}
        <li>{{c['name']}} - {{c['service']}}</li>
    {% endfor %}
    </ul>

    <h2>添加订单</h2>
    <form method="post" action="/add_order">
        客户姓名: <input name="customer">
        收入: <input name="income">
        成本: <input name="cost">
        <button type="submit">添加</button>
    </form>

    <h2>订单列表</h2>
    <ul>
    {% for o in orders %}
        <li>{{o['customer']}} - 利润: {{o['profit']}}</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html, customers=customers, orders=orders)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    customers.append({
        'name': request.form['name'],
        'service': request.form['service']
    })
    return redirect('/')

@app.route('/add_order', methods=['POST'])
def add_order():
    income = float(request.form['income'])
    cost = float(request.form['cost'])
    orders.append({
        'customer': request.form['customer'],
        'profit': income - cost
    })
    return redirect('/')

if __name__ == "__main__":
    app.run()
