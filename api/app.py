import os
import uuid
import requests
from flask import Flask, request, session, jsonify
from flask_cors import CORS

from config import Config

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config.update(SESSION_COOKIE_SAMESITE=None, SESSION_COOKIE_SECURE=False)
CORS(app, supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS)

def require_auth():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return None

@app.route('/api/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    payment_url = f"{Config.PAYMENT_SERVICE_URL}/api/payments/{payment_id}"
    
    try:
        response = requests.get(
            payment_url,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        return response.content, response.status_code, {'Content-Type': 'application/json'}
        
    except requests.exceptions.RequestException:
        return jsonify({
            "success": False, 
            "message": "Payment service unavailable"
        }), 503

@app.route('/api/payments', methods=['POST'])
def payments():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    payment_url = f"{Config.PAYMENT_SERVICE_URL}/api/payments"
    
    try:
        response = requests.post(
            payment_url,
            headers={'Content-Type': 'application/json'},
            json=request.get_json(),
            timeout=10
        )
        
        return response.content, response.status_code, {'Content-Type': 'application/json'}
        
    except requests.exceptions.RequestException:
        return jsonify({
            "success": False, 
            "message": "Payment service unavailable"
        }), 503

@app.route('/api/accounts', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/api/accounts/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_accounts(path):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    url = f"{Config.ACCOUNT_SERVICE_URL}/api/accounts"
    if path:
        url += f"/{path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers={'Content-Type': 'application/json'},
            json=request.get_json() if request.method in ['POST', 'PUT'] else None,
            params=dict(request.args) if request.method == 'GET' else None,
            timeout=10
        )
        
        return response.content, response.status_code, {'Content-Type': 'application/json'}
        
    except requests.exceptions.RequestException:
        return jsonify({"success": False, "message": "Account service unavailable"}), 503

@app.route('/api/billings', defaults={'path': ''}, methods=['GET'])
def proxy_billing(path):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    url = f"{Config.BILLING_SERVICE_URL}/api/billings"
    if path:
        url += f"/{path}"
    
    try:
        response = requests.get(
            url,
            headers={'Content-Type': 'application/json'},
            params=dict(request.args),
            timeout=10
        )
        
        return response.content, response.status_code, {'Content-Type': 'application/json'}
        
    except requests.exceptions.RequestException:
        return jsonify({"success": False, "message": "Billing service unavailable"}), 503

@app.route('/')
def root():
    return jsonify({
        "success": True,
        "message": "Flask API is running",
        "endpoints": ["/api/register", "/api/login", "/api/logout", "/api/profile"]
    })


@app.route('/api/register', methods=['POST'])
def register():
    url = f"{Config.USERS_SERVICE_URL}/api/users"

    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json=request.get_json(),
            timeout=10
        )

        return response.content, response.status_code, {'Content-Type': 'application/json'}
        
    except requests.exceptions.RequestException:
        return jsonify({"success": False, "message": "Service unavailable"}), 503

@app.route('/api/login', methods=['POST'])
def login():
    url = f"{Config.USERS_SERVICE_URL}/api/users"
    json_data = request.get_json()

    email = json_data.get('email')
    password = json_data.get('password')

    try:
        response = requests.get(
            url,
            headers={'Content-Type': 'application/json'},
            params=dict(email=email, password=password),
            timeout=10
        )

        response.encoding = 'utf-8'

        if response.status_code == 200:
            response_data = response.json()
            user = response_data.get('data')
            session.clear()
            session.update(user_id=user['id'], session_token=str(uuid.uuid4()))

            return jsonify(response_data), 200

        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        
    except requests.exceptions.RequestException:
        return jsonify({"success": False, "message": "Service unavailable"}), 503

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True}), 200


@app.route('/api/me', methods=['GET'])
def me():
    auth_error = require_auth()
    if auth_error:
        return auth_error

    url = f"{Config.USERS_SERVICE_URL}/api/users"
    user_id = session.get('user_id')
    if user_id:
        url += f"/{user_id}"
    
    try:
        response = requests.get(
            url,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        return response.content, response.status_code, {'Content-Type': 'application/json'}
        
    except requests.exceptions.RequestException:
        return jsonify({"success": False, "message": "Service unavailable"}), 503

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT)
