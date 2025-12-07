import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

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
login_manager.init_app(app)
login_manager.login_view = 'users_bp.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

from . import views

from .users import users_bp
from .products import products_bp
from .expenses import expenses_bp
from .users.models import User

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
app.register_blueprint(expenses_bp)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
