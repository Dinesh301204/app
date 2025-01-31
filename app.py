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

    # Create the mcq_questions table if it doesn't exist
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

    # Sample data to insert into the table
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
    # Check if the user is a student
    conn = sqlite3.connect('stuusers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stuusers WHERE username = ?', (user,))
    student = cursor.fetchone()
    conn.close()
    
    is_student = student is not None  # True if student, False if staff

    if is_student:
        conn = sqlite3.connect('courses.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
        conn.close()
        staff_courses = []  # Staff users don't see student courses
    else:
        # Fetch courses for staff
        conn = sqlite3.connect('courses.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT course_code, course_name, class
            FROM staff_courses
        ''')
        staff_courses = cursor.fetchall()
        conn.close()
        courses = []  # Staff users don't see student courses

    return render_template('dashboard.html', user=user, is_student=is_student, courses=courses, staff_courses=staff_courses)


@app.route('/course-details/<course_code>/<user>', methods=['GET'])
def course_details(course_code, user):
    # Check if the user is a staff member
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (user,))
    staff = cursor.fetchone()
    conn.close()

    is_staff = staff is not None  # True if staff, False if student

    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    
    if is_staff:
        # Fetch student marks for the selected course
        cursor.execute('SELECT student_name, d_no, marks FROM student_marks WHERE course_code = ?', (course_code,))
        student_marks = cursor.fetchall()
        
        conn.close()
        
        if student_marks:
            return render_template('course_details.html', user=user, is_staff=is_staff, course_code=course_code, student_marks=student_marks)
        else:
            return "No students enrolled for this course", 404  # Handle empty student marks case

    else:
        # Fetch course details for students
        cursor.execute('SELECT * FROM courses WHERE course_code = ?', (course_code,))
        course = cursor.fetchone()

        if not course:
            conn.close()
            return "Course not found", 404

        # Fetch MCQs related to the course
        cursor.execute('SELECT * FROM mcq_questions WHERE course_code = ?', (course_code,))
        mcq_questions = cursor.fetchall()
        conn.close()

        return render_template('course_details.html', user=user, is_staff=is_staff, course=course, mcq_questions=mcq_questions)

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

def create_staff_courses_database():
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            course_name TEXT NOT NULL,
            class TEXT NOT NULL
        )
    ''')

    staff_courses = [
        ('21UCS145F', 'DSA', 'I B.Sc'),
        ('21UCS154G', 'DCF', 'II B.Sc'),
        ('21UCS165H', 'AI', 'III B.Sc')
    ]

    for course in staff_courses:
        cursor.execute('INSERT OR IGNORE INTO staff_courses (course_code, course_name, class) VALUES (?, ?, ?)', course)

    conn.commit()
    conn.close()

def create_student_marks_database():
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            student_name TEXT NOT NULL,
            d_no TEXT NOT NULL,
            marks INTEGER NOT NULL
        )
    ''')

    student_marks = [
        ('21UCS145F', 'Dinesh', '22ucs166', 95),
        ('21UCS145F', 'Kevin', '22ucs165', 93),
        ('21UCS145F', 'John', '22ucs109', 90),
        ('21UCS145F', 'Abi', '22ucs167', 92),
        ('21UCS145F', 'Kiru', '22ucs168', 91)
    ]

    for record in student_marks:
        cursor.execute('INSERT OR IGNORE INTO student_marks (course_code, student_name, d_no, marks) VALUES (?, ?, ?, ?)', record)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    create_student_database()
    create_courses_database()
    create_mcq_database()
    create_student_marks_database()  # ✅ Add this to initialize student marks
    app.run(debug=True)