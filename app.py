from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Aman@123",
        database="student_db"
    )


# 🔹 REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# 🔹 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = user[1]
            return redirect("/")
        else:
            return "❌ Invalid login"

    return render_template("login.html")


# 🔹 LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# 🔹 HOME
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")


# 🔹 ADD STUDENT
@app.route("/add", methods=["POST"])
def add_student():
    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]
    age = request.form["age"]
    course = request.form["course"]
    marks = request.form["marks"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO students (name, age, course, marks) VALUES (%s, %s, %s, %s)",
                   (name, age, course, marks))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/students")


# 🔹 SHOW
@app.route("/students")
def students():
    if "user" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("students.html", students=data)


# 🔹 DELETE
@app.route("/delete/<int:id>")
def delete_student(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/students")


# 🔹 EDIT
@app.route("/edit/<int:id>")
def edit_student(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit.html", student=student)


# 🔹 UPDATE
@app.route("/update/<int:id>", methods=["POST"])
def update_student(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE students SET name=%s, age=%s, course=%s, marks=%s WHERE id=%s",
                   (request.form["name"], request.form["age"], request.form["course"], request.form["marks"], id))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/students")


if __name__ == "__main__":
    app.run(debug=True)