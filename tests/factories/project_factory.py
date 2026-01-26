# tests/factories/project_factory.py
import factory
from datetime import datetime, timedelta
from tests.factories.base_factory import BaseFactory
from tests.factories.category_factory import CategoryFactory
from models.project_model import Project
from domain.projects_enums import Project_status, Project_priority


class ProjectFactory(BaseFactory):
    """Factory para crear proyectos"""
    
    class Meta:
        model = Project
    
    name = factory.Faker("catch_phrase")
    description = factory.Faker("text", max_nb_chars=500)
    deadline = factory.LazyFunction(lambda: datetime.now() + timedelta(days=30))
    status = Project_status.not_assigned
    priority = Project_priority.medium
    category = factory.SubFactory(CategoryFactory)
    
    class Params:
        # Traits para diferentes estados
        assigned = factory.Trait(status=Project_status.assigned)
        completed = factory.Trait(status=Project_status.completed)
        high_priority = factory.Trait(priority=Project_priority.high)
        low_priority = factory.Trait(priority=Project_priority.low)