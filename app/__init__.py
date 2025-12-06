import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

app = Flask(__name__)
app.config.from_pyfile("../config.py")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-please-change")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI',
    'sqlite:///expenses.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

from . import views

from .users import users_bp
from .products import products_bp
from .expenses import expenses_bp

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
app.register_blueprint(expenses_bp)
