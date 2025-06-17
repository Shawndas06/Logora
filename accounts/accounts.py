import sqlite3
from flask import request, jsonify, Flask
from flask_cors import CORS

from config import Config

DB = 'account.db'

app = Flask(__name__)
CORS(app, supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_account_table():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL,
            isActive BOOLEAN NOT NULL DEFAULT 1,
            address TEXT NOT NULL,
            ownerFullName TEXT NOT NULL,
            propertySquare REAL NOT NULL,
            residentsCount INTEGER NOT NULL,
            companyName TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_account_table()


@app.route('/api/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    required = ['number', 'address', 'ownerFullName', 'propertySquare', 'residentsCount', 'companyName']
    if not all(field in data for field in required):
        return jsonify({"success": False, "message": "Не все поля заполнены"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO accounts (number, isActive, address, ownerFullName, propertySquare, residentsCount, companyName)
        VALUES (?, 1, ?, ?, ?, ?, ?)
    ''', (
        data['number'],
        data['address'],
        data['ownerFullName'],
        data['propertySquare'],
        data['residentsCount'],
        data['companyName']
    ))
    conn.commit()
    account_id = cursor.lastrowid
    new_account = conn.execute('SELECT * FROM accounts WHERE id = ?', (account_id,)).fetchone()
    conn.close()
    return jsonify({"success": True, "data": dict(new_account)}), 201


@app.route('/api/accounts', methods=['GET'])
def list_accounts():
    conn = get_db()
    rows = conn.execute('SELECT * FROM accounts').fetchall()
    conn.close()
    accounts = [dict(row) for row in rows]
    return jsonify({"success": True, "data": accounts})


@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    conn = get_db()
    conn.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route('/api/accounts/<int:account_id>', methods=['PUT'])
def update_account_status(account_id):
    data = request.get_json()
    if 'isActive' not in data:
        return jsonify({"success": False, "message": "Missing isActive field"}), 400

    conn = get_db()
    conn.execute('UPDATE accounts SET isActive = ? WHERE id = ?', (int(data['isActive']), account_id))
    conn.commit()
    updated = conn.execute('SELECT * FROM accounts WHERE id = ?', (account_id,)).fetchone()
    conn.close()
    if not updated:
        return jsonify({"success": False, "message": "Account not found"}), 404

    return jsonify({"success": True, "data": dict(updated)})

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT)
