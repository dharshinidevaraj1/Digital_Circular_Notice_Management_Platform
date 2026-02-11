from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
app = Flask(__name__)
app.secret_key = "hackathon_secret"

# ---------------- MYSQL CONFIG ----------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dharshini20'
app.config['MYSQL_DB'] = 'digital_circular'

mysql = MySQL(app)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Add your login logic here
        # For now, just redirect to admin
        session['role'] = 'student'
        return redirect('/dashboard')
    
    return render_template('login.html')

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM circulars ORDER BY created_at DESC")
    circulars = cur.fetchall()
    cur.close()

    return render_template('admin.html', circulars=circulars)
if __name__ == '__main__':
    app.run(debug=True)

