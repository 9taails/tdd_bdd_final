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

# pylint: disable=too-few-public-methods

"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from service.models import Product, Category

CATEGORIES = [i for i in Category]
PRODUCTS = ["socks", "car", "headphones", "screwdriver", "headlight", "blender", "kettle", "blouse", "shirt", 
           "apple", "banana", "pear"]

class ProductFactory(factory.Factory):
    """Creates fake products for testing"""

    global CATEGORIES
    global PRODUCTS

    class Meta:
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.fuzzy.FuzzyChoice(choices=PRODUCTS)
    description = factory.Faker("sentence", nb_words=5)
    price = factory.fuzzy.FuzzyDecimal(5.00, 50.00)
    available = factory.fuzzy.FuzzyChoice(choices=[True, False])
    category = factory.fuzzy.FuzzyChoice(choices=CATEGORIES)

