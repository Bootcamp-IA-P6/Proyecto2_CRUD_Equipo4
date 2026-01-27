
import factory
from factory.declarations import  LazyAttribute, SubFactory
from tests.factories.base_factory import BaseFactory
from tests.factories.project_factory import ProjectFactory
from tests.factories.skill_factory import SkillFactory
from tests.models.project_skill import ProjectSkill


class ProjectSkillFactory(BaseFactory):
    """Factory para crear relaciones project-skill"""
    
    class Meta:
        model = ProjectSkill
    
    project = factory.SubFactory(ProjectFactory)
    skill = factory.SubFactory(SkillFactory)

    # Solo asignamos los IDs al crear el objeto
    @factory.lazy_attribute
    def project_id(self):
        return self.project.id

    @factory.lazy_attribute
    def skill_id(self):
        return self.skill.id
    deleted_at = None