import sqlite3
from flask import request, jsonify, Flask
from flask_cors import CORS
from collections import defaultdict

DB = 'billing.db'

app = Flask(__name__)
CORS(app, supports_credentials=True)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_billing_table():
    conn = get_db()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL,
        type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    conn.commit()
    conn.close()

init_billing_table()

def transform_bills(bills):
    service_totals = defaultdict(float)
    total_amount = 0
    
    for bill in bills:
        service_type = bill['type']
        amount = bill['amount']
        service_totals[service_type] += amount
        total_amount += amount
    
    total_services = [
        {'type': service_type, 'amount': amount} 
        for service_type, amount in service_totals.items()
    ]
    
    result = {
        'services': bills,
        'total': {
            'services': total_services,
            'amount': total_amount
        }
    }
    
    return result

@app.route('/api/billings', methods=['GET'])
def get_billing():
    args = request.args
    account_id = args.get('account')
    period = args.get('period') or 6

    if not account_id:
        return jsonify({"success": False, "message": "Не указан идентификатор аккаунта"}), 400

    if not period.isdigit() or int(period) <= 0:
        return jsonify({"success": False, "message": "Период должен быть положительным числом"}), 400

    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "DB connection failed"}), 500

    rows = conn.execute(f'SELECT * FROM bills WHERE account_id = ? AND created_at >= date("now", "-{period} months")', (account_id,)).fetchall()
    conn.close()

    bills = [{
        'id': row['id'],
        'accountId': row['account_id'],
        'createdAt': row['created_at'],
        'status': row['status'],
        'type': row['type'],
        'amount': row['amount'],
    } for row in rows]

    return jsonify({"success": True, "data": transform_bills(bills)}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
