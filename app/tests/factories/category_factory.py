
from factory.declarations import Sequence
from factory.faker import Faker
from app.tests.factories.base_factory import BaseFactory
from app.models.category_model import Category


class CategoryFactory(BaseFactory):
    """Factory para crear categorías"""
    
    class Meta:
        model = Category
    
    name = Sequence(lambda n: f"category_{n}")
    description = Faker("text", max_nb_chars=200)