from flask import Blueprint, render_template, request, redirect, flash
import re
from databases import get_db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE login_id=?", (login_id,)).fetchone()

        # Verify user exists and password hash matches
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid Login ID or Password", "error")
            return redirect("/login")

        flash("Logged in successfully", "success")
        return redirect("/dashboard")

    return render_template("login.html", title="Login")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        login_id = request.form["login_id"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        db = get_db()

        # login id validation
        if len(login_id) < 6 or len(login_id) > 12:
            flash("Login ID must be 6–12 characters.", "error")
            return redirect("/signup")

        exists = db.execute("SELECT * FROM users WHERE login_id=?", (login_id,)).fetchone()
        if exists:
            flash("Login ID already exists", "error")
            return redirect("/signup")

        # email validation
        if not re.match(r".+@.+\..+", email):
            flash("Invalid email format", "error")
            return redirect("/signup")

        # password validation
        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect("/signup")

        # Password strength: require at least one lowercase, one uppercase,
        # one special (non-alphanumeric) character, and length > 8.
        # Note: interpreting "more than length 8" as minimum length 9.
        pwd_pattern = r'(?=.*[a-z])(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{9,}'
        if not re.match(pwd_pattern, password):
            flash(
                "Password must be at least 9 characters and include uppercase, lowercase, and a special character.",
                "error",
            )
            return redirect("/signup")

        # Store password securely as a hash
        pw_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (login_id, email, password) VALUES (?, ?, ?)",
            (login_id, email, pw_hash),
        )
        db.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect("/login")

    return render_template("signup.html", title="Sign Up")
