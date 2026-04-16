from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

customers = []
orders = []

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

    <div class="card">客户总数：{{ customers|length }}</div>
    <div class="card">订单总数：{{ orders|length }}</div>
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
        <tr>
            <th>姓名</th>
            <th>电话</th>
            <th>业务</th>
            <th>操作</th>
        </tr>
        {% for c in customers %}
        <tr>
            <td>{{ c.name }}</td>
            <td>{{ c.phone }}</td>
            <td>{{ c.service }}</td>
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
        <tr>
            <th>客户</th>
            <th>业务</th>
            <th>收入</th>
            <th>成本</th>
            <th>利润</th>
            <th>操作</th>
        </tr>
        {% for o in orders %}
        <tr>
            <td>{{ o.customer }}</td>
            <td>{{ o.service }}</td>
            <td>{{ o.income }}</td>
            <td>{{ o.cost }}</td>
            <td>{{ o.profit }}</td>
            <td><a href="/delete_order/{{ loop.index0 }}">删除</a ></td>
        </tr>
        {% endfor %}
    </table>

    <h2>业务利润统计</h2>
    <table>
        <tr>
            <th>业务类型</th>
            <th>利润</th>
        </tr>
        {% for s in service_types %}
        <tr>
            <td>{{ s }}</td>
            <td>
                {{
                    orders
                    | selectattr("service", "equalto", s)
                    | map(attribute="profit")
                    | sum
                }}
            </td>
        </tr>
        {% endfor %}
    </table>

</body>
</html>
"""

@app.route('/')
def home():
    total_profit = sum(order['profit'] for order in orders)
    return render_template_string(
        html,
        customers=customers,
        orders=orders,
        total_profit=total_profit,
        service_types=service_types
    )

@app.route('/add_customer', methods=['POST'])
def add_customer():
    customers.append({
        'name': request.form['name'],
        'phone': request.form['phone'],
        'service': request.form['service']
    })
    return redirect('/')

@app.route('/delete_customer/<int:index>')
def delete_customer(index):
    if 0 <= index < len(customers):
        customers.pop(index)
    return redirect('/')

@app.route('/add_order', methods=['POST'])
def add_order():
    income = float(request.form['income'])
    cost = float(request.form['cost'])
    orders.append({
        'customer': request.form['customer'],
        'service': request.form['service'],
        'income': income,
        'cost': cost,
        'profit': income - cost
    })
    return redirect('/')

@app.route('/delete_order/<int:index>')
def delete_order(index):
    if 0 <= index < len(orders):
        orders.pop(index)
    return redirect('/')

if __name__ == "__main__":
    app.run()
