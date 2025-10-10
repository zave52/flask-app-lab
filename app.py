from flask import Flask, render_template, url_for, redirect, Response
from datetime import datetime

app = Flask(__name__)


@app.context_processor
def inject_current_year() -> dict[str, int]:
    return {'current_year': datetime.now().year}


@app.route("/")
def main() -> Response:
    return redirect(url_for("resume"))


@app.route("/resume")
def resume() -> str:
    return render_template("resume.html")


@app.route("/contacts")
def contacts() -> str:
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
