from flask import Flask, render_template, request, redirect, url_for
from flask_mysql_connector import MySQL
import uuid

app = Flask(__name__)

# Configuration MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE'] = 'flaskapp'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('acceuil.html')


# Méthode pour la gestion de la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard', role=user['role']))
    return render_template('login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM requests")
    requests = cursor.fetchall()
    cursor.close()
    return render_template('admin_dashboard.html', requests=requests)


@app.route('/dashboard/<role>')
def dashboard(role):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM requests WHERE role=%s OR service=%s", (role, role))
    user_requests = cursor.fetchall()
    cursor.close()
    return render_template('dashboard.html', role=role, requests=user_requests)


@app.route('/new_request/<role>', methods=['GET', 'POST'])
def new_request(role):
    if request.method == 'POST':
        article = request.form['article']
        quantity = request.form['quantity']
        date = request.form['date']
        service = request.form['service']
        status = 'en cours'

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO requests (id, article, quantity, date, status, role, service)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (str(uuid.uuid4()), article, quantity, date, status, role, service))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('dashboard', role=role))
    return render_template('new_request.html', role=role)


@app.route('/process_request/<req_id>/<role>', methods=['POST'])
def process_request(req_id, role):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE requests SET status='traité' 
        WHERE id=%s AND service=%s AND status='en cours'
    """, (req_id, role))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('dashboard', role=role))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
