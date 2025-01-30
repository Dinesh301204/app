CREATE TABLE mcq_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT,
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT
);

CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    course_code TEXT,
    question_id INTEGER,
    selected_answer TEXT
);
