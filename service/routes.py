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

    #
    # Uncomment this line of code once you implement READ A PRODUCT
    #
    # location_url = url_for("get_products", product_id=product.id, _external=True)
    location_url = "/"  # delete once READ is implemented
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################

@app.route(f"/products", methods=["GET"])
def list_all_product():
    """
    Retrieve multiple Products
    This endpoint will return all the Products
    """
    app.logger.info("Request to Retrieve all the Products")

    name = request.args.get('name')
    category = request.args.get('category')
    availability = request.args.get('availability')

    if name:
        app.logger.info("Find by name: %s", name)
        prods = Product.find_by_name(name)

    elif category:
        app.logger.info("Find by name: %s", category)
        category_value = getattr(Category, category.upper())
        prods = Product.find_by_category(category_value)

    elif availability:
        app.logger.info("Find by availability: %s", availability)
        prods = Product.find_by_availability(availability)
    
    else:
        app.logger.info("Find all")
        prods = Product.all()
    
    if not prods:
        abort(404)
    the_products = [prod.serialize() for prod in prods]
    
    return jsonify(the_products), status.HTTP_200_OK


######################################################################
# U P D A T E   A   P R O D U C T
######################################################################

@app.route(f"/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """
    Update a single Product
    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")

    prod = Product.find(product_id)
    if not prod:
        abort(404)
    req = request.get_json()
    prod.deserialize(req)
    prod.id = product_id
    prod.update()
    the_product = prod.serialize()
    
    return jsonify(the_product), status.HTTP_200_OK



######################################################################
# R E A D   A   P R O D U C T
######################################################################

@app.route(f"/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Retrieve a single Product
    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)

    prod = Product.find(product_id)
    if not prod:
        abort(404)
    the_product = prod.serialize()
    
    return jsonify(the_product), status.HTTP_200_OK

######################################################################
# D E L E T E   A   P R O D U C T
######################################################################


@app.route(f"/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Retrieve a single Product
    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request to Delete a product with id [%s]", product_id)

    prod = Product.find(product_id)
    if not prod:
        abort(404)
    prod.delete()
    
    return jsonify({'message':"The product with name {prod.name} successfully deleted"}), status.HTTP_200_OK

