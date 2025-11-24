# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_get_a_product(self):
        """ It should Read a product from the db """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        app.logger.info("Creating %s", product)
        product.id = None
        product.create()
        self.assertNotEqual(product.id, None)
        # Check db has 1 item
        products = Product.all()
        self.assertEqual(len(products), 1)
        product_db = Product.find(product.id)
        self.assertEqual(product_db.name, product.name)
        self.assertEqual(product_db.description, product.description)
        self.assertEqual(product_db.price, product.price)
        self.assertEqual(product_db.available, product.available)
        self.assertEqual(product_db.category, product.category)

    def test_update_a_product(self):
        """ It should Update an existing product from the db """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

        # Create a new product
        product = ProductFactory()
        logging.debug("Creating %s", product)
        product.id = None
        product.create()
        self.assertNotEqual(product.id, None)
        logging.info("Created %s", product)

        # Update the created product
        products = Product.all()
        product_db = products[0]
        product_db.description = "This is an updated description."
        product_db.update()
        logging.info("Updated %s", product)

        # Check db still has 1 item
        self.assertEqual(len(products), 1)

        # Check the updated product
        products = Product.all()
        product_db = products[0]
        self.assertEqual(product_db.id, product.id)
        self.assertEqual(product_db.description, "This is an updated description.")

    def test_delete_a_product(self):
        """ It should Delete an existing product from the db """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

        # Create a new product
        product = ProductFactory()
        logging.debug("Creating %s", product)
        product.id = None
        product.create()
        self.assertNotEqual(product.id, None)
        logging.info("Created %s", product)

        # Check db has 1 item
        products = Product.all()
        self.assertEqual(len(products), 1)

        # Delete the product
        product_db = products[0]
        product_db.delete()
        logging.info("Deleted %s", product)

        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

    def test_list_all_products(self):
        """ It should return all existing products in the db """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

        product_list = []

        # Create 5 new products
        for _ in range(5):
            product = ProductFactory()
            logging.debug("Creating %s", product)
            product.id = None
            product.create()
            self.assertNotEqual(product.id, None)
            logging.info("Created %s", product)
            product_list.append(product)

        # Check db has 5 items
        products = Product.all()
        self.assertEqual(len(products), 5)

        # Check the items match
        self.assertEqual(products, product_list)

    def test_get_product_by_name(self):
        """ It should return products with a specific name """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

        # Create 15 new products
        for _ in range(15):
            product = ProductFactory()
            logging.debug("Creating %s", product)
            product.id = None
            product.create()
            self.assertNotEqual(product.id, None)
            logging.info("Created %s", product)

        # Check db has 15 items
        products = Product.all()
        self.assertEqual(len(products), 15)

        # Retrieve the product by name
        product_db = products[0]
        name = product_db.name
        found = Product.find_by_name(name)
        products_count = len([p for p in products if p.name == name])
        found_count = len(list(found))

        self.assertEqual(found_count, products_count)
        self.assertEqual(found[0].name, name)

    def test_get_product_by_availability(self):
        """ It should return available products """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

        # Create 15 new products
        for _ in range(15):
            product = ProductFactory()
            product.create()
            logging.info("Created %s", product)

        # Check db has 15 items
        products = Product.all()
        self.assertEqual(len(products), 15)

        # Retrieve the product by availability
        product_db = products[0]
        available = product_db.available
        found = Product.find_by_availability(available)
        products_count = len([p for p in products if p.available == available])
        found_count = len(list(found))

        self.assertEqual(found_count, products_count)
        self.assertEqual(found[0].available, available)

    def test_get_product_by_category(self):
        """ It should return products in given category """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

        # Create 15 new products
        for _ in range(15):
            product = ProductFactory()
            product.create()
            logging.info("Created %s", product)

        # Check db has 15 items
        products = Product.all()
        self.assertEqual(len(products), 15)

        # Retrieve the product by category
        product_db = products[0]
        cat = product_db.category
        found = Product.find_by_category(cat)
        products_count = len([p for p in products if p.category == cat])
        found_count = len(list(found))

        self.assertEqual(found_count, products_count)
        self.assertEqual(found[0].category, cat)

    def test_get_product_by_price(self):
        """ It should return products with a given price """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

        # Create 15 new products
        for _ in range(15):
            product = ProductFactory()
            product.create()
            logging.info("Created %s", product)
            logging.info("Price is %s", product.price)

        # Check db has 15 items
        products = Product.all()
        self.assertEqual(len(products), 15)

        # Retrieve the product with same price
        product_db = products[0]
        price = product_db.price
        found = Product.find_by_price(price)
        products_count = len([p for p in products if p.price == price])
        found_count = len(list(found))
        logging.info("Found %s", found)

        self.assertEqual(found_count, products_count)
        self.assertEqual(found[0].price, price)

    def test_convert_str_price_to_float(self):
        """ It should convert a price format from string to a float """
        # Check db is empty
        products = Product.all()
        self.assertEqual(products, [])

        # Create a new product
        product = ProductFactory()
        product.create()
        logging.info("Created %s", product)

        # Update the created product
        products = Product.find_by_price(str(product.price))
        product_db = products[0]
        self.assertIsInstance(product_db.price, Decimal)

    def test_wrong_available_value_type(self):
        """ It should return DataValidationError for non-boolean types in available """
        # Create a product dictionary
        product = ProductFactory()
        product_dict = {
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "available": "True",
            "category": "UNKNOWN"
        }
        self.assertRaises(DataValidationError, Product.deserialize, product, product_dict)

    def test_attribute_error(self):
        """ It should return AttributeError for accessing non-existent attribute """
        product = Product()

        with self.assertRaises(AttributeError):
            product.deserialize({"name": product.new_name})

    def test_key_error(self):
        """ It should return DataValidationError for passing data with missing attribute """
        # Create a product dictionary
        product = ProductFactory()
        product_dict = {
            "name": product.name,
            "new_name": "some_name"
        }
        logging.debug("Processing %s", product)
        self.assertRaises(DataValidationError, Product.deserialize, product, product_dict)

    def test_type_error(self):
        """ It should return DataValidationError for accessing non-existent attribute """
        product = Product()
        product_dict = None

        with self.assertRaises(DataValidationError):
            product.deserialize(product_dict)

    def test_update_with_wrong_id(self):
        """ It should return DataValidationError for updating a product with incorrect id """
        # Create a new product
        product = ProductFactory()
        product.create()
        logging.info("Created %s", product)

        # Update the created product
        products = Product.all()
        product_db = products[0]
        product_db.id = None
        self.assertRaises(DataValidationError, product_db.update)
