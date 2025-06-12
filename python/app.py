import os
from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from forms import LoginForm, RegisterForm
from flask_wtf import CSRFProtect

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
    users = conn.execute('SELECT id, username FROM users').fetchall()
    conn.close()
    return render_template('team.html', users=users)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    if user is None:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('login'))
    # Mock data for profile template
    user_dict = {
        'full_name': user['username'],
        'email': f"{user['username']}@example.com"
    }
    accounts = [
        {'number': '12345', 'address': 'ул. Примерная, д. 1', 'area': 50, 'residents': 2, 'management_company': 'УК Пример'},
        {'number': '67890', 'address': 'ул. Тестовая, д. 2', 'area': 75, 'residents': 4, 'management_company': 'УК Тест'}
    ]
    payments = [
        {'period': 'Октябрь 2025', 'amount': 5000},
        {'period': 'Ноябрь 2025', 'amount': 5500}
    ]
    return render_template('profile.html', full_name=user_dict['full_name'], email=user_dict['email'], accounts=accounts, payments=payments)

if __name__ == '__main__':
    app.run(debug=True)