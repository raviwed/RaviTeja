from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import secrets

# def generate_api_key():
#     return secrets.token_urlsafe(32)

app = Flask(__name__)

DATABASE = 'students.db'
app.secret_key = secrets.token_hex(32)


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# def insert_api_key():
#     key = generate_api_key()
#     conn = get_db_connection()
#     conn.execute("INSERT INTO api_keys (key) VALUES (?)", (key,))
#     conn.commit()
#     conn.close()
#     return key




# Initialize DB
def init_db():
    
    conn = get_db_connection()
    # conn.execute('''
    # CREATE TABLE IF NOT EXISTS api_keys (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     key TEXT NOT NULL UNIQUE,
    #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    # )
    # ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            marks INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    existing = conn.execute("SELECT COUNT(*) FROM teachers").fetchone()[0]
    if existing == 0:
        conn.execute("INSERT INTO teachers (username, password) VALUES (?, ?)", ('admin', 'admin123'))
        conn.execute("INSERT INTO teachers (username, password) VALUES (?, ?)", ('teacher1', 'pass1'))
    conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM teachers WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()
        if user:
            session['teacher'] = username
            return redirect('/home')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/home')
def home():
    if 'teacher' not in session:
        return redirect('/')
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('home.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data['name']
    subject = data['subject']
    marks = int(data['marks'])

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE name = ? AND subject = ?', (name, subject)).fetchone()
    if student:
        new_marks = student['marks'] + marks
        conn.execute('UPDATE students SET marks = ? WHERE id = ?', (new_marks, student['id']))
    else:
        conn.execute('INSERT INTO students (name, subject, marks) VALUES (?, ?, ?)', (name, subject, marks))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted'})

@app.route('/edit_student/<int:id>', methods=['POST'])
def edit_student(id):
    data = request.get_json()
    name = data['name']
    subject = data['subject']
    marks = int(data['marks'])

    conn = get_db_connection()
    conn.execute('UPDATE students SET name = ?, subject = ?, marks = ? WHERE id = ?', 
                 (name, subject, marks, id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'updated'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
