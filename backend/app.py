import os
from flask import Flask, redirect
from routes.auth import auth
import databases

# Point Flask to the frontend templates/static directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Secret key for session flashing; use env var in production
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Register DB teardown and ensure DB/tables exist
databases.init_app(app)
databases.init_db()

# (OTP/SMTP configuration removed) If you re-enable password-reset via email,
# configure SMTP and OTP settings here using environment variables as needed.

app.register_blueprint(auth)

@app.route("/")
def home():
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
