from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import traceback
import base64
import io

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
    if session.get('role') != 'user':
        return redirect('/')

    sort = request.args.get('sort')

    cur = mysql.connection.cursor()

    if sort == 'old':
        cur.execute("SELECT * FROM circulars ORDER BY created_at ASC")
    else:
        cur.execute("SELECT * FROM circulars ORDER BY created_at DESC")

    circulars = cur.fetchall()
    cur.close()

    return render_template('user.html', circulars=circulars)

# ---------------- STATS DASHBOARD ----------------
import matplotlib.pyplot as plt
@app.route('/stats')
def stats():
    if session.get('role') != 'user':
        return redirect('/')

    cur = mysql.connection.cursor()

    # Priority distribution
    cur.execute("SELECT priority, COUNT(*) FROM circulars GROUP BY priority")
    priority_data = cur.fetchall()

    priorities = []
    counts = []

    for row in priority_data:
        priorities.append(row[0])
        counts.append(row[1])

    # Generate bar chart
    plt.figure(figsize=(6,4))
    plt.bar(priorities, counts)
    plt.title("Circular Priority Distribution")
    plt.xlabel("Priority")
    plt.ylabel("Count")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    plt.close()

    # Circular count over time
    cur.execute("SELECT DATE(created_at), COUNT(*) FROM circulars GROUP BY DATE(created_at)")
    time_data = cur.fetchall()

    dates = []
    date_counts = []

    for row in time_data:
        dates.append(str(row[0]))
        date_counts.append(row[1])

    plt.figure(figsize=(6,4))
    plt.plot(dates, date_counts, marker='o')
    plt.title("Circulars Over Time")
    plt.xlabel("Date")
    plt.ylabel("Count")

    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()

    plt.close()
    cur.close()

    return render_template('stats.html', plot_url=plot_url, plot_url2=plot_url2)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    print("Starting Flask app on http://127.0.0.1:5000")
    app.run(debug=True)
