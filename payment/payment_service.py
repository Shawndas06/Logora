import sqlite3
import time
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)

DB_PATH = 'payment.db'
BILLING_URL = 'http://charges-service:5001/api/billing/complete'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def make_response(success, data=None, status_code=200):
    payload = {'success': success}
    if data:
        payload.update(data)
    return jsonify(payload), status_code

# --- Initialize database ---
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            billing_ids TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('processing','completed','error')),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')
    conn.commit()
    conn.close()

# --- Background simulation ---
def simulate_payment(payment_id, account_id, cc_number):
    time.sleep(2)
    status = 'completed'
    # Simulate credit card error
    if cc_number.replace(' ', '') == '4111111111111112':
        status = 'error'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE payments SET status = ? WHERE id = ?', (status, payment_id))
    conn.commit()
    conn.close()

    if status == 'completed':
        try:
            requests.post(BILLING_URL, json={'account_id': account_id, 'payment_id': payment_id})
        except requests.RequestException:
            pass

@app.route('/payments', methods=['POST'])
def create_payment():
    if not request.is_json:
        return make_response(False, {'error': 'Content-Type must be application/json'}, 400)
    data = request.get_json(silent=True)
    if data is None:
        return make_response(False, {'error': 'Invalid JSON payload'}, 400)

    account_id = data.get('account')
    billing_ids = data.get('billingIds')
    amount = data.get('amount')
    credit_card = data.get('creditCard')

    # Validation
    if account_id is None or billing_ids is None or amount is None:
        return make_response(False, {'error': 'Fields account, billingIds, amount'}, 400)
    if not isinstance(billing_ids, list) or not all(isinstance(i, int) for i in billing_ids):
        return make_response(False, {'error': 'billingIds must be a list of integers'}, 400)
    if not isinstance(amount, (int, float)) or amount <= 0:
        return make_response(False, {'error': 'Amount must be a positive number'}, 400)
    """ cc_number = credit_card.get('number') """
    """ if not isinstance(cc_number, str): """
    """     return make_response(False, {'error': 'creditCard.number must be a string'}, 400) """

    # Insert payment record
    billing_ids_str = ','.join(str(i) for i in billing_ids)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO payments (account_id, billing_ids, amount, status) VALUES (?, ?, ?, ?)',
            (account_id, billing_ids_str, amount, 'processing')
        )
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        return make_response(False, {'error': f'Database error: {e}'}, 500)

    # Start background thread
    threading.Thread(target=simulate_payment, args=(payment_id, account_id, cc_number), daemon=True).start()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE payments SET status = ? WHERE id = ?',
        ('completed', payment_id)
    )
    conn.commit()
    conn.close()

    return make_response(True, {'payment_id': payment_id}, 201)

@app.route('/payments', methods=['GET'])
def get_all_payments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, account_id, billing_ids, amount, status, created_at FROM payments')
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        return make_response(False, {'error': f'Database error: {e}'}, 500)

    payments = [
        {
            'id': row['id'],
            'accountId': row['account_id'],
            'billingIds': row['billing_ids'].split(','),
            'amount': row['amount'],
            'status': row['status'],
            'createdAt': row['created_at']
        }
        for row in rows
    ]
    return make_response(True, {'payments': payments}, 200)

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
