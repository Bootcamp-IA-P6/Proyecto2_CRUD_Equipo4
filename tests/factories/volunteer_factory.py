# tests/factories/volunteer_factory.py
import factory
from tests.factories.base_factory import BaseFactory
from tests.factories.user_factory import UserFactory
from models.volunteers_model import Volunteer
from domain.volunteer_enum import VolunteerStatus


class VolunteerFactory(BaseFactory):
    """Factory para crear voluntarios"""
    
    class Meta:
        model = Volunteer
    
    status = VolunteerStatus.active
    
    @factory.lazy_attribute
    def user_id(self):
        user = UserFactory()
        return user.id
    
    class Params:
        # Traits para diferentes estados
        inactive = factory.Trait(status=VolunteerStatus.inactive)
        suspended = factory.Trait(status=VolunteerStatus.suspended)