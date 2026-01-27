from factory.declarations import LazyAttribute, Sequence
from tests.factories.base_factory import BaseFactory
from tests.factories.user_factory import UserFactory
from models.volunteers_model import Volunteer
from domain.volunteer_enum import VolunteerStatus


class VolunteerFactory(BaseFactory):
    """Factory para crear voluntarios"""
    
    class Meta:
        model = Volunteer
    
    status = VolunteerStatus.active
    
   
    user_id = LazyAttribute(lambda obj: UserFactory.create().id)