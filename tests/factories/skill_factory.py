# tests/factories/skill_factory.py
import factory
from factory.declarations import Sequence
from tests.factories.base_factory import BaseFactory
from models.skill_model import Skill


class SkillFactory(BaseFactory):
    """Factory para crear skills"""
    
    class Meta:
        model = Skill
    
    name = Sequence(lambda n: f"skill_{n}")