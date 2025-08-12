from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# PostgreSQL credentials from environment variables
postgres_username = os.getenv('TG_POSTGRES_USERNAME')
postgres_password = os.getenv('TG_POSTGRES_PASSWORD')
postgres_db = os.getenv('TG_POSTGRES_DB')
postgres_host = os.getenv('TG_POSTGRES_HOST')
postgres_port = os.getenv('TG_POSTGRES_PORT')

# PostgreSQL connection
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{postgres_username}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Dummy admin user
class Admin(UserMixin):
    id = 1
    username = os.getenv('TG_ADMIN_USERNAME')
    password = os.getenv('TG_ADMIN_PASSWORD')

@login_manager.user_loader
def load_user(user_id):
    return Admin()

# Updated SQLAlchemy model
class TelegramUser(db.Model):
    __tablename__ = 'telegram_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == Admin.username and request.form["password"] == Admin.password:
            login_user(Admin())
            return redirect(url_for("dashboard"))
        return "Invalid credentials", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        username = request.form["username"]
        if username:
            new_user = TelegramUser(username=username)
            db.session.add(new_user)
            db.session.commit()
    users = TelegramUser.query.order_by(TelegramUser.id.desc()).all()
    return render_template("dashboard.html", users=users)

@app.route("/delete/<int:id>")
@login_required
def delete_user(id):
    user = TelegramUser.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)