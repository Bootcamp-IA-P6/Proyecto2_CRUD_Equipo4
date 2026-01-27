from factory.declarations import LazyAttribute, Sequence
from app.tests.factories.base_factory import BaseFactory
from app.tests.factories.user_factory import UserFactory
from app.models.volunteers_model import Volunteer
from app.domain.volunteer_enum import VolunteerStatus


class VolunteerFactory(BaseFactory):
    """Factory para crear voluntarios"""
    
    class Meta:
        model = Volunteer
    
    status = VolunteerStatus.active
    
   
    user_id = LazyAttribute(lambda obj: UserFactory.create().id)