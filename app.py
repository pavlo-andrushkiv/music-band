from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)


# Моделі бази даних
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)


def custom_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return decorated_view


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash("You have been logged in!", "success")
            return redirect(url_for("home"))
        else:
            flash(
                "Login unsuccessful. Please check your username and password.", "danger"
            )
    return render_template("login.html")


# Додана сторінка реєстрації
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists. Please choose a different one.", "danger")
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Your account has been created! You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
@custom_login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# Додана кнопка логін/логаут у навігаційній панелі
@app.context_processor
def inject_login_logout():
    if current_user.is_authenticated:
        login_logout_text = "Logout"
        login_logout_url = url_for("logout")
    else:
        login_logout_text = "Login"
        login_logout_url = url_for("login")
    return dict(login_logout_text=login_logout_text, login_logout_url=login_logout_url)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/albums")
def albums():
    all_albums = Album.query.all()
    return render_template("albums.html", albums=all_albums)


@app.route("/album/<int:album_id>")
def album(album_id):
    album = Album.query.get_or_404(album_id)
    return render_template("album.html", album=album)


@app.route("/album/add", methods=["GET", "POST"])
@custom_login_required
def add_album():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        new_album = Album(title=title, description=description)
        db.session.add(new_album)
        db.session.commit()
        return redirect(url_for("albums"))
    return render_template("add_album.html")


@app.route("/album/edit/<int:album_id>", methods=["GET", "POST"])
@custom_login_required
def edit_album(album_id):
    album = Album.query.get_or_404(album_id)
    if request.method == "POST":
        album.title = request.form["title"]
        album.description = request.form["description"]
        db.session.commit()
        return redirect(url_for("albums"))
    return render_template("edit_album.html", album=album)


@app.route("/album/delete/<int:album_id>", methods=["POST"])
@custom_login_required
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    return redirect(url_for("albums"))


if __name__ == "__main__":
    app.run(debug=True)
