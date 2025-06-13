import os
import sqlite3
import uuid
import requests
from flask import Flask, request, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config.update(SESSION_COOKIE_SAMESITE=None, SESSION_COOKIE_SECURE=False)
CORS(app, supports_credentials=True)

ACCOUNT_SERVICE_URL = os.getenv('ACCOUNT_SERVICE_URL', 'http://account:5001')
BILLING_SERVICE_URL = os.getenv('BILLING_SERVICE_URL', 'http://billing:5002')
PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://payment:5003')
REPORT_SERVICE_URL = os.getenv('REPORT_SERVICE_URL', 'http://report:5004')

DB = 'db.sqlite3'

def require_auth():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return None

def get_db():
    try:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        return None


def init_db():
    conn = get_db()
    if conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
        conn.commit()
        conn.close()


init_db()

# TODO: Implement full function to handle payments while calling billing service!
@app.route('/api/payments', methods=['GET', 'POST'])
def payments():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    payment_url = f"{PAYMENT_SERVICE_URL}/payments"
    billing_url = f"{BILLING_SERVICE_URL}/api/billings"
    
    try:
        headers = {'Content-Type': 'application/json'}
        
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(payment_url, headers=headers, json=request.get_json())
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": "Payment service unavailable"}), 503

@app.route('/api/accounts', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/api/accounts/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_accounts(path):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    url = f"{ACCOUNT_SERVICE_URL}/api/accounts"
    if path:
        url += f"/{path}"
    
    try:
        headers = {'Content-Type': 'application/json'}
        
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.get_json())
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.get_json())
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": "Account service unavailable"}), 503

@app.route('/api/billings', defaults={'path': ''}, methods=['GET'])
def proxy_billing(path):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    url = f"{BILLING_SERVICE_URL}/api/billings"
    if path:
        url += f"/{path}"
    
    try:
        headers = {'Content-Type': 'application/json'}
        
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.get_json())
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.get_json())
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": "Account service unavailable"}), 503

@app.route('/')
def root():
    return jsonify({
        "success": True,
        "message": "Flask API is running",
        "endpoints": ["/api/register", "/api/login", "/api/logout", "/api/profile"]
    })


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        return jsonify({"success": False, "message": "Email or password missing"}), 400

    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "DB connection failed"}), 500

    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                     (email, generate_password_hash(password)))
        conn.commit()
        return jsonify({"success": True}), 200
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists"}), 409
    finally:
        conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        return jsonify({"success": False, "message": "Email or password missing"}), 400

    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "DB connection failed"}), 500

    user = conn.execute('SELECT * FROM users WHERE username = ?', (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session.clear()
        session.update(user_id=user['id'], username=user['username'], session_token=str(uuid.uuid4()))
        return jsonify({"success": True, "data": dict(user) }), 200

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True}), 200


@app.route('/api/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "DB connection failed"}), 500

    user = conn.execute('SELECT id, username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if not user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    return jsonify({
        "success": True,
        "data": dict(user)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
