import factory
from tests.factories.base_factory import BaseFactory
from tests.factories.volunteer_factory import VolunteerFactory
from tests.factories.skill_factory import SkillFactory
from tests.models.volunteer_skill import VolunteerSkill


class VolunteerSkillFactory(BaseFactory):
    """Factory para crear relaciones volunteer-skill"""
    
    class Meta:
        model = VolunteerSkill
    
    
    volunteer_id = factory.LazyFunction(lambda: VolunteerFactory().id)
    skill_id = factory.LazyFunction(lambda: SkillFactory().id)
    deleted_at = None