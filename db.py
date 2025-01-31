from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


app = Flask(__name__)

def create_mcq_database():
    conn = sqlite3.connect('mcq_questions.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
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

    # Insert sample MCQ questions
    questions = [
        ('21UCS123A54', 'What is DSA?', 'Data Science Algorithms', 'Data Structures and Algorithms', 'Data Science Application', 'Database Systems', 'b'),
        ('21UCS123A54', 'What is the time complexity of binary search?', 'O(1)', 'O(log n)', 'O(n)', 'O(n^2)', 'b'),
        ('21UCS123A54', 'Which data structure is used for implementing recursion?', 'Queue', 'Stack', 'Linked List', 'Array', 'b')
    ]

    for question in questions:
        cursor.execute('INSERT OR IGNORE INTO mcq_questions (course_code, question, option_a, option_b, option_c, option_d, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?)', question)

    conn.commit()
    conn.close()

# Run this when starting the Flask app
if __name__ == '__main__':
    create_mcq_database()  # ✅ Run this to create the missing table # Ensure student marks table exists
    app.run(debug=True)
