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
    def test_read_a_product(self):
        """It should test the representational str of the product object"""
        prod = ProductFactory()
        # logging(f"A Factirial Product was created: {prod}")
        prod.id = None
        prod.create()
        self.assertFalse(prod.id == None)
        prod_obj = Product.find(product_id=prod.id)
        self.assertEqual(prod_obj.id, prod.id)
        self.assertEqual(prod_obj.name, prod.name)
        self.assertEqual(prod_obj.description, prod.description)
        self.assertEqual(prod_obj.price, prod.price)
        self.assertEqual(prod_obj.available, prod.available)
        self.assertEqual(prod_obj.category, prod.category)
        
    def test_update_a_product(self):
        """It shoud create a product, update it, and asssert the changes are correct & there is just one object"""
        prod = ProductFactory()
        # logging(f"A Factirial Product was created: {prod}")
        prod.id = None
        prod.create()
        db_prod = Product.find(prod.id)
        fake_prod = ProductFactory()
        db_prod.id = fake_prod.id
        db_prod.description = fake_prod.description
        origin_id = db_prod.id
        db_prod.update()
        self.assertEqual(db_prod.id, prod.id)
        self.assertEqual(db_prod.description, fake_prod.description)
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, origin_id)
        self.assertEqual(products[0].description, db_prod.description)

    def test_update_a_product_no_id(self):
        """It will check a sad path for no id update"""
        product = ProductFactory()
        product.create()
        products = Product.all()
        # Verify there is a product
        self.assertEqual(len(products), 1)
        products[0].id = None
        self.assertRaises(DataValidationError, products[0].update)


    

        
        
    def test_delete_a_product(self):
        """It should create a product, delete it and check there is no objetcs"""
        fact_prod = ProductFactory()
        # logging(f"A Factorial product was create - {fact_prod}")
        fact_prod.id = None
        fact_prod.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        prod = products[0] if products else self.assertTrue(products)
        prod.delete()
        products_after_delete = Product.all()
        self.assertEqual(len(products_after_delete), 0)
        
        
    def test_list_products(self):
        """It should create products and list theme correctlly"""
        self.assertEqual(Product.all(), [])
        fact_prod = ProductFactory.build_batch(5)
        for i in range(5):
            fact_prod[i].id = None
            fact_prod[i].create()    
        # logging(f"A Factorial products was create - {fact_prod}")
        self.assertEqual(len(Product.all()), 5)
        
        
    def test_find_products_by_name(self):
        """It should create products and find theme by name"""
        self.assertEqual(Product.all(), [])
        fact_prod = ProductFactory.build_batch(5)
        fake_prod_1_name = fact_prod[0].name
        num_of_name_fake_prod = len([prod for prod in fact_prod if prod.name == fake_prod_1_name])
        for i in range(5):
            fact_prod[i].id = None
            fact_prod[i].create()    
        # logging(f"A Factorial products was create - {fact_prod}")
        self.assertEqual(len(Product.all()), 5)
        products = Product.find_by_name(fake_prod_1_name)
        self.assertEqual(len(list(products)), num_of_name_fake_prod)
        for prod in products:
            self.assertEqual(prod.name, fake_prod_1_name)
            
            
    def test_find_products_by_availability(self):
        """It should create products and find theme by availability"""
        self.assertEqual(Product.all(), [])
        fact_prod = ProductFactory.build_batch(5)
        availability = fact_prod[0].available
        num_availability = len([prod for prod in fact_prod if prod.available == availability])
        for i in range(5):
            fact_prod[i].id = None
            fact_prod[i].create()    
        # logging(f"A Factorial products was create - {fact_prod}")
        self.assertEqual(len(list(Product.all())), 5)
        products = Product.find_by_availability(availability)
        self.assertEqual(len(list(products)), num_availability)
        for prod in products:
            self.assertEqual(prod.available, availability)
            
    
    def test_find_products_by_category(self):
        """It should create products and find theme by category"""
        self.assertEqual(Product.all(), [])
        fact_prod = ProductFactory.build_batch(5)
        category = fact_prod[0].category
        num_category = len([prod for prod in fact_prod if prod.category == category])
        for i in range(5):
            fact_prod[i].id = None
            fact_prod[i].create()    
        # logging(f"A Factorial products was create - {fact_prod}")
        self.assertEqual(len(Product.all()), 5)
        products = Product.find_by_category(category)
        self.assertEqual(len(list(products)), num_category)
        for prod in products:
            self.assertEqual(prod.category, category)
        

    def test_deserialize_bad_available_type(self):
        """A sad path to test a non boolean avaliable type"""
        prod = ProductFactory()
        prod.available = 1
        prod.update()
        prod_dict = prod.serialize()
        p = ProductFactory()
        self.assertRaises(DataValidationError, p.deserialize(prod_dict))

    def test_find_products_by_price(self):
        """It should create products and find theme by price"""
        self.assertEqual(Product.all(), [])
        fact_prod = ProductFactory.build_batch(5)
        price = fact_prod[0].price
        num_price = len([prod for prod in fact_prod if prod.price == price])
        for i in range(5):
            fact_prod[i].id = None
            fact_prod[i].create()    
        # logging(f"A Factorial products was create - {fact_prod}")
        self.assertEqual(len(Product.all()), 5)
        products = Product.find_by_price(price)
        self.assertEqual(len(list(products)), num_price)
        for prod in products:
            self.assertEqual(prod.price, price)

        