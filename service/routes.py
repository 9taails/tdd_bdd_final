######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from decimal import Decimal
from flask import jsonify, request, abort
from flask import url_for  # noqa: F401 pylint: disable=unused-import
from service.models import Product, Category
from service.common import status  # HTTP Status Codes
from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################


@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################


@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################


@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    location_url = url_for("get_a_product", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################


@app.route("/products", methods=["GET"])
def list_products():
    """ Returns a list of all products from the db or sorted by given attribute"""

    app.logger.info("Getting all products...")

    products = []

    # Filtering names
    product_name = request.args.get("name")
    category_name = request.args.get("category")
    product_available = request.args.get("available")
    product_price = request.args.get("price")

    if product_name:
        app.logger.info("Filtering items by name: %s", product_name)
        products = Product.find_by_name(product_name)

    elif category_name:
        app.logger.info("Filtering items by category: %s", category_name)
        category = getattr(Category, category_name.upper())
        products = Product.find_by_category(category)

    elif product_available:
        app.logger.info("Filtering items by status: %s", product_available)
        available_value = product_available.lower() in ["true", "yes", "1"]
        products = Product.find_by_availability(available_value)

    elif product_price:
        app.logger.info("Filtering items by price: %s", product_price)
        products = Product.find_by_price(Decimal(product_price))

    else:
        app.logger.info("Returning a list of all items.")
        products = Product.all()

    product_list = [p.serialize() for p in products]

    return product_list, status.HTTP_200_OK

######################################################################
# R E A D   A   P R O D U C T
######################################################################


@app.route("/products/<int:product_id>", methods=['GET'])
def get_a_product(product_id):
    """ Retrieve a product from the database by product id. """

    product = Product.find(product_id)

    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    
    message = product.serialize()
    return jsonify(message), status.HTTP_200_OK


######################################################################
# U P D A T E   A   P R O D U C T
######################################################################


@app.route("/products/<int:product_id>", methods=['PUT'])
def update_a_product(product_id):
    """ Update an existing product in the database by product id. """

    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)

    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    data = request.get_json()   # Json update
    product.deserialize(data)   # Updated dict
    product.id = product_id
    product.update()
    return jsonify(product.serialize()), status.HTTP_200_OK

######################################################################
# D E L E T E   A   P R O D U C T
######################################################################


@app.route("/products/<int:product_id>", methods=['DELETE'])
def delete_a_product(product_id):
    """ Delete an existing product in the database by product id. """

    app.logger.info("Request to Delete a product with id [%s]", product_id)

    product = Product.find(product_id)

    if product:
        product.delete()
        app.logger.info("Deleted ", product.name)
        return {"message": "Product deleted."}, status.HTTP_200_OK

    return {"message": "Product with given ID not found."}, status.HTTP_404_NOT_FOUND
