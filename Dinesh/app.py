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

def create_courses_database():
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            course_name TEXT NOT NULL,
            staff_handling TEXT NOT NULL
        )
    ''')

    courses = [
        ('21UCS123A54', 'DSA', 'DR.AROCKIAM'),
        ('21UCS123A54', 'DCF', 'DR.GGRR'),
        ('21UCS123A54', 'AI', 'DR.CHARLES'),
        ('21UCS123A54', 'CC', 'DR.BRITTO')
    ]

    for course in courses:
        cursor.execute('INSERT OR IGNORE INTO courses (course_code, course_name, staff_handling) VALUES (?, ?, ?)', course)

    conn.commit()
    conn.close()

def create_mcq_database():
    conn = sqlite3.connect('mcq_questions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mcq_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL
        )
    ''')

    questions = [
        ('21UCS123A54', 'What is DSA?', 'Data Science Algorithms', 'Data Structures and Algorithms', 'Data Science Application', 'Database Systems', 'b'),
        ('21UCS123A54', 'What is the time complexity of binary search?', 'O(1)', 'O(log n)', 'O(n)', 'O(n^2)', 'b'),
        ('21UCS123A54', 'Which data structure is used for implementing recursion?', 'Queue', 'Stack', 'Linked List', 'Array', 'b')
    ]

    for question in questions:
        cursor.execute('INSERT OR IGNORE INTO mcq_questions (course_code, question, option_a, option_b, option_c, option_d, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?)', question)

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
    conn = sqlite3.connect('stuusers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stuusers WHERE username = ?', (user,))
    student = cursor.fetchone()
    conn.close()

    is_student = student is not None  # True if the user is a student, False if staff

    if is_student:
        conn = sqlite3.connect('courses.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
        conn.close()

        conn = sqlite3.connect('mcq_questions.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM mcq_questions')
        mcq_questions = cursor.fetchall()
        conn.close()
    else:
        courses = []  # Staff users don't see courses
        mcq_questions = []  # Staff users don't see MCQs

    return render_template('dashboard.html', user=user, is_student=is_student, courses=courses, mcq_questions=mcq_questions)

@app.route('/course-details/<course_code>/<user>', methods=['GET', 'POST'])
def course_details(course_code, user):
    # Fetch the course details from the courses database
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM courses WHERE course_code = ?', (course_code,))
    course = cursor.fetchone()
    conn.close()

    # Fetch the MCQs related to the course from the MCQ database
    conn = sqlite3.connect('mcq_questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mcq_questions WHERE course_code = ?', (course_code,))
    mcq_questions = cursor.fetchall()
    conn.close()

    if course:
        return render_template('course_details.html', course=course, mcq_questions=mcq_questions, user=user)
    else:
        return "Course not found", 404

@app.route('/exam/<course_code>/<user>', methods=['GET', 'POST'])
def exam(course_code, user):
    conn = sqlite3.connect('mcq_questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mcq_questions WHERE course_code = ?', (course_code,))
    questions = cursor.fetchall()
    conn.close()
    
    if request.method == 'POST':
        conn = sqlite3.connect('responses.db')
        cursor = conn.cursor()

        for question in questions:
            question_id = question[0]
            selected_answer = request.form.get(f'question_{question_id}')
            cursor.execute('INSERT INTO responses (user, course_code, question_id, selected_answer) VALUES (?, ?, ?, ?)',
                           (user, course_code, question_id, selected_answer))
        
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard', user=user))

    return render_template('exam.html', user=user, course_code=course_code, questions=questions)

if __name__ == '__main__':
    create_database()
    create_student_database()
    create_courses_database()  # Add this to initialize the courses database
    create_mcq_database()  # Create MCQ database
    app.run(debug=True)
