from flask import (
    request,
    redirect,
    url_for,
    render_template,
    flash,
    session,
    make_response
)

from . import users_bp

VALID_USERS = {
    "admin": "password123",
    "user": "pass456"
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

    if request.method == "POST":
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
        return redirect(url_for("users_bp.login"))

    cookies = request.cookies.to_dict()

    current_theme = request.cookies.get("theme", "light")

    return render_template(
        "users/profile.html",
        username=username,
        cookies=cookies,
        theme=current_theme
    )


@users_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Ви успішно вийшли з системи", "info")
    return redirect(url_for("users_bp.login"))


@users_bp.route("/add_cookie", methods=["POST"])
def add_cookie():
    username = session.get("username")
    if not username:
        flash("Будь ласка, увійдіть в систему", "warning")
        return redirect(url_for("users_bp.login"))

    cookie_key = request.form.get("cookie_key")
    cookie_value = request.form.get("cookie_value")
    cookie_max_age = request.form.get("cookie_max_age")

    if not cookie_key or not cookie_value:
        flash("Ключ та значення cookie є обов'язковими", "error")
        return redirect(url_for("users_bp.profile"))

    max_age = int(cookie_max_age) if cookie_max_age else 3600

    response = make_response(redirect(url_for("users_bp.profile")))
    response.set_cookie(cookie_key, cookie_value, max_age=max_age)

    flash(
        f"Cookie '{cookie_key}' успішно додано (термін дії: {max_age} секунд)",
        "success"
    )
    return response


@users_bp.route("/delete_cookie", methods=["POST"])
def delete_cookie():
    username = session.get("username")
    if not username:
        flash("Будь ласка, увійдіть в систему", "warning")
        return redirect(url_for("users_bp.login"))

    cookie_key = request.form.get("cookie_key")

    if not cookie_key:
        flash("Вкажіть ключ cookie для видалення", "error")
        return redirect(url_for("users_bp.profile"))

    if cookie_key not in request.cookies:
        flash(f"Cookie '{cookie_key}' не знайдено", "warning")
        return redirect(url_for("users_bp.profile"))

    response = make_response(redirect(url_for("users_bp.profile")))
    response.delete_cookie(cookie_key)

    flash(f"Cookie '{cookie_key}' успішно видалено", "info")
    return response


@users_bp.route("/delete_all_cookies", methods=["POST"])
def delete_all_cookies():
    username = session.get("username")
    if not username:
        flash("Будь ласка, увійдіть в систему", "warning")
        return redirect(url_for("users_bp.login"))

    all_cookies = request.cookies.to_dict()

    if not all_cookies:
        flash("Немає cookies для видалення", "warning")
        return redirect(url_for("users_bp.profile"))

    response = make_response(redirect(url_for("users_bp.profile")))

    cookies_count = 0
    for cookie_key in all_cookies.keys():
        if not cookie_key.startswith("session"):
            response.delete_cookie(cookie_key)
            cookies_count += 1

    flash(f"Видалено {cookies_count} cookie(s)", "info")
    return response


@users_bp.route("/set_theme/<string:theme>")
def set_theme(theme):
    username = session.get("username")
    if not username:
        flash("Будь ласка, увійдіть в систему", "warning")
        return redirect(url_for("users_bp.login"))

    valid_themes = ["light", "dark"]
    if theme not in valid_themes:
        flash("Невірна кольорова схема", "error")
        return redirect(url_for("users_bp.profile"))

    response = make_response(redirect(url_for("users_bp.profile")))
    response.set_cookie("theme", theme, max_age=30 * 24 * 60 * 60)

    theme_name = "темну" if theme == "dark" else "світлу"
    flash(f"Кольорову схему змінено на {theme_name}", "success")
    return response
