from flask import Blueprint

users_bp = Blueprint(
    "users_bp",
    __name__,
    url_prefix="/users",
    template_folder="templates"
)

from . import views
