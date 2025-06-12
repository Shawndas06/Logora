import os
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from forms import LoginForm, RegisterForm
from flask_wtf import CSRFProtect
from pdf_generator import create_receipt
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)  # Secure random key
csrf = CSRFProtect(app)

DATABASE = 'db.sqlite3'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        flash(f'Ошибка подключения к базе данных: {e}', 'error')
        raise

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Вход выполнен успешно', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = generate_password_hash(password)
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Регистрация прошла успешно, теперь войдите', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Имя пользователя уже занято', 'error')
    return render_template('registrat.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))

@app.route('/team')
def team():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, full_name, email FROM users').fetchall()
    conn.close()
    return render_template('team.html', users=users)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    # Get user's accounts
    accounts = conn.execute('''
        SELECT * FROM accounts 
        WHERE user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    # Get charges and payments for each account
    accounts_data = []
    for account in accounts:
        charges = conn.execute('''
            SELECT * FROM charges 
            WHERE account_id = ? 
            ORDER BY start_date DESC
        ''', (account['id'],)).fetchall()
        
        payments = conn.execute('''
            SELECT * FROM payments 
            WHERE account_id = ? 
            ORDER BY date DESC
        ''', (account['id'],)).fetchall()
        
        accounts_data.append({
            'account': account,
            'charges': charges,
            'payments': payments
        })
    
    conn.close()
    
    if user is None:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login'))
    
    return render_template('profile.html', 
                         user=user,
                         accounts_data=accounts_data)

@app.route('/generate_receipt/<int:account_id>')
def generate_receipt(account_id):
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('login'))
    
    try:
        receipt_path, qr_path = create_receipt(account_id)
        return send_file(receipt_path, as_attachment=True, download_name=f'receipt_{account_id}.pdf')
    except Exception as e:
        flash(f'Ошибка при генерации квитанции: {str(e)}', 'error')
        return redirect(url_for('profile'))

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    conn = get_db_connection()
    accounts = conn.execute('''
        SELECT a.*, 
               (SELECT SUM(amount) FROM charges WHERE account_id = a.id) as total_charges,
               (SELECT SUM(amount) FROM payments WHERE account_id = a.id) as total_payments
        FROM accounts a
        WHERE user_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return {'accounts': [dict(account) for account in accounts]}

@app.route('/api/charges/<int:account_id>', methods=['GET'])
def get_charges(account_id):
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    conn = get_db_connection()
    charges = conn.execute('''
        SELECT c.* 
        FROM charges c
        JOIN accounts a ON c.account_id = a.id
        WHERE a.user_id = ? AND c.account_id = ?
        ORDER BY c.start_date DESC
    ''', (session['user_id'], account_id)).fetchall()
    conn.close()
    
    return {'charges': [dict(charge) for charge in charges]}

@app.route('/api/payments/<int:account_id>', methods=['GET'])
def get_payments(account_id):
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
    
    conn = get_db_connection()
    payments = conn.execute('''
        SELECT p.* 
        FROM payments p
        JOIN accounts a ON p.account_id = a.id
        WHERE a.user_id = ? AND p.account_id = ?
        ORDER BY p.date DESC
    ''', (session['user_id'], account_id)).fetchall()
    conn.close()
    
    return {'payments': [dict(payment) for payment in payments]}

if __name__ == '__main__':
    app.run(debug=True)