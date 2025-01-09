from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection, create_tables

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Initialize the database tables
create_tables()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the username already exists
        existing_user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('signup'))

        # Insert new user
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        conn.commit()
        conn.close()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', 
                            (username, password, role)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']

            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials or role. Please try again.')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Access denied.")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    timetable = conn.execute('SELECT * FROM timetable').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', timetable=timetable)

@app.route('/create_timetable', methods=['GET', 'POST'])
def create_timetable():
    if session.get('role') != 'admin':
        flash("Access denied.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        class_name = request.form['class_name']
        day = request.form['day']
        time = request.form['time']
        course = request.form['course']
        faculty = request.form['faculty']

        conn = get_db_connection()
        conn.execute('INSERT INTO timetable (class_name, day, time, course, faculty) VALUES (?, ?, ?, ?, ?)',
                     (class_name, day, time, course, faculty))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    return render_template('create_timetable.html')

@app.route('/edit_timetable/<int:id>', methods=['GET', 'POST'])
def edit_timetable(id):
    if session.get('role') != 'admin':
        flash("Access denied.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    timetable_entry = conn.execute('SELECT * FROM timetable WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        class_name = request.form['class_name']
        day = request.form['day']
        time = request.form['time']
        course = request.form['course']
        faculty = request.form['faculty']

        conn.execute('UPDATE timetable SET class_name = ?, day = ?, time = ?, course = ?, faculty = ? WHERE id = ?',
                     (class_name, day, time, course, faculty, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    conn.close()
    return render_template('edit_timetable.html', entry=timetable_entry)

@app.route('/delete_timetable/<int:id>', methods=['POST'])
def delete_timetable(id):
    if session.get('role') != 'admin':
        flash("Access denied.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM timetable WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        flash("Access denied.")
        return redirect(url_for('login'))
    return render_template('student_dashboard.html')

@app.route('/view_timetable/<class_name>')
def view_timetable(class_name):
    if session.get('role') != 'student':
        flash("Access denied.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    timetable = conn.execute('SELECT * FROM timetable WHERE class_name = ?', (class_name,)).fetchall()
    conn.close()
    return render_template('timetable_view.html', timetable=timetable, class_name=class_name)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
