from flask import (
    request,
    redirect,
    url_for,
    render_template,
    flash,
    make_response
)
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from . import users_bp
from .models import User
from sqlalchemy import select


@users_bp.route("/hi/<name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template("users/hi.html", name=name, age=age)


@users_bp.route("/admin")
def admin():
    to_url = url_for(
        "users_bp.greetings",
        name="administrator",
        age=45,
        _external=True
    )
    print(to_url)
    return redirect(to_url)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users_bp.profile"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember", False)

        stmt = select(User).filter_by(username=username)
        user = db.session.execute(stmt).scalars().first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Logged in successfully!", "success")

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for("users_bp.profile"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("users_bp.login"))

    return render_template("users/login.html")


@users_bp.route("/profile")
@login_required
def profile():
    cookies = request.cookies.to_dict()
    current_theme = request.cookies.get("theme", "light")

    return render_template(
        "users/profile.html",
        username=current_user.username,
        cookies=cookies,
        theme=current_theme
    )


@users_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully", "info")
    return redirect(url_for("users_bp.login"))


@users_bp.route("/add_cookie", methods=["POST"])
@login_required
def add_cookie():
    cookie_key = request.form.get("cookie_key")
    cookie_value = request.form.get("cookie_value")
    cookie_max_age = request.form.get("cookie_max_age")

    if not cookie_key or not cookie_value:
        flash("Cookie key and value are required", "error")
        return redirect(url_for("users_bp.profile"))

    max_age = int(cookie_max_age) if cookie_max_age else 3600

    response = make_response(redirect(url_for("users_bp.profile")))
    response.set_cookie(cookie_key, cookie_value, max_age=max_age)

    flash(
        f"Cookie '{cookie_key}' added successfully (max age: {max_age} seconds)",
        "success"
    )
    return response


@users_bp.route("/delete_cookie", methods=["POST"])
@login_required
def delete_cookie():
    cookie_key = request.form.get("cookie_key")

    if not cookie_key:
        flash("Specify a cookie key to delete", "error")
        return redirect(url_for("users_bp.profile"))

    if cookie_key not in request.cookies:
        flash(f"Cookie '{cookie_key}' not found", "warning")
        return redirect(url_for("users_bp.profile"))

    response = make_response(redirect(url_for("users_bp.profile")))
    response.delete_cookie(cookie_key)

    flash(f"Cookie '{cookie_key}' deleted successfully", "info")
    return response


@users_bp.route("/delete_all_cookies", methods=["POST"])
@login_required
def delete_all_cookies():
    all_cookies = request.cookies.to_dict()

    if not all_cookies:
        flash("No cookies to delete", "warning")
        return redirect(url_for("users_bp.profile"))

    response = make_response(redirect(url_for("users_bp.profile")))

    cookies_count = 0
    for cookie_key in all_cookies.keys():
        if not cookie_key.startswith("session"):
            response.delete_cookie(cookie_key)
            cookies_count += 1

    flash(f"Deleted {cookies_count} cookie(s)", "info")
    return response


@users_bp.route("/set_theme/<string:theme>")
@login_required
def set_theme(theme):
    valid_themes = ["light", "dark"]
    if theme not in valid_themes:
        flash("Invalid theme", "error")
        return redirect(url_for("users_bp.profile"))

    response = make_response(redirect(url_for("users_bp.profile")))
    response.set_cookie("theme", theme, max_age=30 * 24 * 60 * 60)

    theme_name = "dark" if theme == "dark" else "light"
    flash(f"Theme changed to {theme_name}", "success")
    return response


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users_bp.profile"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
            flash("All fields are required", "error")
            return redirect(url_for("users_bp.register"))

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("users_bp.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return redirect(url_for("users_bp.register"))

        stmt = select(User).filter_by(username=username)
        existing_user = db.session.execute(stmt).scalars().first()

        if existing_user:
            flash("A user with that username already exists", "error")
            return redirect(url_for("users_bp.register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in", "success")
        return redirect(url_for("users_bp.login"))

    return render_template("users/register.html")
