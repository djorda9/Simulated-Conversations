# tests.py
import random
import string

import factory
from django.test import TestCase

import models


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))

#create one for each model
class ResearchFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Researcher

    name = factory.LazyAttribute(lambda t: random_string())
    description = factory.LazyAttribute(lambda t: random_string())


class ResearcherTestCase(TestCase):

    def test_something(self):
        # Get a completely random thing
        thing = ResearcherFactory.create()
        # Test assertions would go here

    def test_something_else(self):
        # Get a thing with an explicit name
        thing = ThingFactory.create(name='Foo')
        # Test assertions would go here

