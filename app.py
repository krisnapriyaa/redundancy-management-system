from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = "kp_super_secret_key"

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Balram*5Krisna',
    database='redundancy_db',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/login_user', methods=['POST'])
def login_user():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == "admin" and password == "admin123":
        session['user'] = username
        return redirect(url_for('home'))

    return "Invalid Credentials"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    existing = cursor.fetchone()

    if existing:
        return jsonify({"message": "Duplicate data detected!"}), 409

    cursor.execute(
        "INSERT INTO users (name, email, phone) VALUES (%s, %s, %s)",
        (name, email, phone)
    )

    return jsonify({"message": "User added successfully!"}), 201

@app.route('/get_users', methods=['GET'])
def get_users():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify(users)

@app.route('/search_user', methods=['GET'])
def search_user():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    query = request.args.get('query', '')

    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE name LIKE %s OR email LIKE %s",
        (f"%{query}%", f"%{query}%")
    )

    users = cursor.fetchall()
    return jsonify(users)

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))

    if cursor.rowcount == 0:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"message": "User deleted successfully!"}), 200

@app.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')

    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET name=%s, phone=%s WHERE id=%s",
        (name, phone, user_id)
    )

    if cursor.rowcount == 0:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"message": "User updated successfully!"}), 200

if __name__ == "__main__":
    app.run()