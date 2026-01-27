import factory
from factory.declarations import  Sequence
from tests.factories.base_factory import BaseFactory
from models import Role


class RoleFactory(BaseFactory):
    """Factory para crear roles"""
    
    class Meta:
        model = Role
    
    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"role_{n}") 
    
    @classmethod
    def admin(cls, **kwargs):
        """Crea el rol Admin con ID 1"""
        return cls.create(id=1, name="Admin", **kwargs)
    
    @classmethod
    def default(cls, **kwargs):
        """Crea el rol Default con ID 2"""
        return cls.create(id=2, name="Default", **kwargs)