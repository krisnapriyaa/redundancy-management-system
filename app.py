from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # User Authentication Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    # Data Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- SECURITY ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required():
    if "user" not in session:
        return False
    return True

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO auth_users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
        except:
            flash("Username already exists!")
        finally:
            conn.close()

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM auth_users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            session["role"] = user["role"]
            flash("Login successful!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return render_template("dashboard.html", users=users)

# ---------------- ADD USER ----------------
@app.route("/add_user", methods=["POST"])
def add_user():
    if not login_required():
        return redirect(url_for("login"))

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone)
        )
        conn.commit()
        flash("User added successfully!")
    except:
        flash("Duplicate email detected!")

    conn.close()
    return redirect(url_for("dashboard"))

# ---------------- SEARCH ----------------
@app.route("/search", methods=["POST"])
def search():
    if not login_required():
        return redirect(url_for("login"))

    keyword = request.form["keyword"]

    conn = get_db()
    users = conn.execute(
        "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?",
        ('%' + keyword + '%', '%' + keyword + '%')
    ).fetchall()
    conn.close()

    return render_template("dashboard.html", users=users)

# ---------------- DELETE USER ----------------
@app.route("/delete/<int:id>")
def delete_user(id):
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash("User deleted successfully!")
    return redirect(url_for("dashboard"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)