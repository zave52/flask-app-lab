from flask import request, redirect, url_for, render_template, flash, session

from . import users_bp

VALID_USERS = {
    'admin': 'password123',
    'user': 'pass456'
}


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
    if "username" in session:
        return redirect(url_for("users_bp.profile"))

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if username in VALID_USERS and VALID_USERS[username] == password:
            session["username"] = username
            flash("Успішний вхід в систему!", "success")
            return redirect(url_for("users_bp.profile"))
        else:
            flash("Невірне ім'я користувача або пароль", "error")
            return redirect(url_for("users_bp.login"))

    return render_template("users/login.html")


@users_bp.route("/profile")
def profile():
    username = session.get("username")

    if not username:
        flash("Будь ласка, увійдіть в систему", "warning")
        return redirect(url_for('users_bp.login'))

    return render_template("users/profile.html", username=username)


@users_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Ви успішно вийшли з системи", "info")
    return redirect(url_for("users_bp.login"))
