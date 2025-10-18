import os

from flask import Flask

app = Flask(__name__)
app.config.from_pyfile("../config.py")
app.secret_key = os.getenv("SECRET_KEY")

from . import views

from .users import users_bp
from .products import products_bp

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
