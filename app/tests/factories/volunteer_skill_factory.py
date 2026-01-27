import factory
from app.tests.factories.base_factory import BaseFactory
from app.tests.factories.volunteer_factory import VolunteerFactory
from app.tests.factories.skill_factory import SkillFactory
from app.tests.models.volunteer_skill import VolunteerSkill


class VolunteerSkillFactory(BaseFactory):
    """Factory para crear relaciones volunteer-skill"""
    
    class Meta:
        model = VolunteerSkill
    
    
    volunteer_id = factory.LazyFunction(lambda: VolunteerFactory().id)
    skill_id = factory.LazyFunction(lambda: SkillFactory().id)
    deleted_at = None