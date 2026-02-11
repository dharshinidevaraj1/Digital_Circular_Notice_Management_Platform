from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import traceback

app = Flask(__name__)
app.secret_key = "hackathon_secret"

# ---------------- MYSQL CONFIG ----------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dharshini20'   # your password
app.config['MYSQL_DB'] = 'digital_circular'

try:
    mysql = MySQL(app)
except Exception as e:
    print(f"MySQL Connection Error: {e}")
    traceback.print_exc()
    mysql = None


# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']

            if mysql is None:
                return "Database connection error. Please contact admin."

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

        except Exception as e:
            return f"Login error: {str(e)}"

    return render_template('login.html')


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/')

    if mysql is None:
        return "Database connection error"

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM circulars ORDER BY created_at DESC")
        circulars = cur.fetchall()
        cur.close()

        return render_template('admin.html', circulars=circulars)

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- USER DASHBOARD ----------------
@app.route('/user')
def user():
    # 🔥 FIXED ROLE CHECK HERE
    if session.get('role') != 'user':
        return redirect('/')

    if mysql is None:
        return "Database connection error"

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM circulars ORDER BY created_at DESC")
        circulars = cur.fetchall()
        cur.close()

        return render_template('user.html', circulars=circulars)

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    print("Starting Flask app on http://127.0.0.1:5000")
    app.run(debug=True)
