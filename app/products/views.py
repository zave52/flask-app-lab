from flask import render_template, abort

from . import products_bp

products = [
    {
        "id": 1,
        "name": "Lemon",
        "description": "A tart, yellow citrus fruit used for juice and zest."
    },
    {
        "id": 2,
        "name": "Apple",
        "description": "A sweet, crunchy fruit commonly eaten fresh or in desserts."
    },
    {
        "id": 3,
        "name": "Banana",
        "description": "A soft, sweet tropical fruit with a creamy texture."
    },
    {
        "id": 4,
        "name": "Orange",
        "description": "A juicy citrus fruit rich in vitamin C."
    }
]


@products_bp.route("")
def get_products():
    return render_template("products/products.html", products=products)


@products_bp.route("/<int:id>")
def detail_product(id):
    if id > len(products) or id < 1:
        abort(404)
    product = products[id - 1]
    return render_template("products/product.html", product=product)
