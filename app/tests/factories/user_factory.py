from factory.declarations import Sequence, LazyAttribute
from factory.faker import Faker
from app.tests.factories.base_factory import BaseFactory
from app.tests.factories.role_factory import RoleFactory
from app.models.users_model import User


class UserFactory(BaseFactory):
    """Factory para crear usuarios"""
    
    class Meta:
        model = User
    
    name = Faker("name")
    email = Sequence(lambda n: f"user{n}@test.com")
    password = Faker("password")
    phone = Sequence(lambda n: f"600000{n:03}")
    birth_date = Faker("date_of_birth", minimum_age=18, maximum_age=65)
    
    role = LazyAttribute(lambda obj: _get_or_create_default_role())


def _get_or_create_default_role():
    """Obtiene o crea el rol por defecto"""
    from app.tests.factories.base_factory import get_session
    from app.models.role_model import Role
    
    session = get_session()  
    if session:
       
        role = session.query(Role).filter(Role.id == 2).first()
        if not role:
            role = RoleFactory.default()
        return role
    return None