# tests/factories/category_factory.py
import factory
from tests.factories.base_factory import BaseFactory
from models.category_model import Category


class CategoryFactory(BaseFactory):
    """Factory para crear categorías"""
    
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f"category_{n}")
    description = factory.Faker("text", max_nb_chars=200)