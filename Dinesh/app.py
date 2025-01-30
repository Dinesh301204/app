from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

def create_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    staff_users = [
        ('Arockiam', '123'),
        ('Mahesh', '456'),
        ('Jude', '678'),
        ('Vimal', '789')
    ]
    
    for username, password in staff_users:
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        cursor.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    
    conn.commit()
    conn.close()

def create_student_database():
    conn = sqlite3.connect('stuusers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stuusers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    student_users = [
        ('Dinesh', '123'),
        ('Kevin', '456'),
        ('Kiruthick', '678'),
        ('Abi', '789')
    ]
    
    for username, password in student_users:
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        cursor.execute('INSERT OR IGNORE INTO stuusers (username, password) VALUES (?, ?)', (username, hashed_password))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/staff-login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            return redirect(url_for('dashboard', user=username))
        else:
            return render_template('staff_login.html', error='Invalid credentials')
    return render_template('staff_login.html')

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect('stuusers.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM stuusers WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            return redirect(url_for('dashboard', user=username))
        else:
            return render_template('student_login.html', error='Invalid credentials')
    return render_template('student_login.html')

@app.route('/dashboard/<user>')
def dashboard(user):
    return render_template('dashboard.html', user=user)

if __name__ == '__main__':
    create_database()
    create_student_database()
    app.run(debug=True)
