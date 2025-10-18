from flask import Blueprint

products_bp = Blueprint(
    "products_bp",
    __name__,
    url_prefix="/products",
    template_folder="templates"
)

from . import views
