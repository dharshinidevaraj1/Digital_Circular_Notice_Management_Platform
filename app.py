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

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[4]

            if user[4] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/user')
        else:
            return "Invalid Credentials"

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

@app.route('/user')
def user():
    if session.get('role') != 'student':
        return redirect('/')
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM circulars ORDER BY created_at DESC")
    circulars = cur.fetchall()
    cur.close()
    
    return render_template('user.html', circulars=circulars)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)