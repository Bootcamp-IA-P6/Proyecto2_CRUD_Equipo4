# tests/factories/project_factory.py
import factory
from factory.declarations import  LazyAttribute, Sequence
from factory.faker import Faker
from datetime import datetime, timedelta, timezone
from tests.factories.base_factory import BaseFactory
from models.project_model import Project
from domain.projects_enums import Project_status, Project_priority


class ProjectFactory(BaseFactory):
    """Factory para crear proyectos"""
    
    class Meta:
        model = Project
    
    name = Sequence(lambda n: f"Project {n}")
    description = Faker("text", max_nb_chars=500)
    deadline = LazyAttribute(lambda obj: datetime.now(timezone.utc) + timedelta(days=30))
    status = Project_status.not_assigned
    priority = Project_priority.medium
    
    @LazyAttribute
    def category(self):
        from tests.factories.base_factory import get_session
        from models.category_model import Category
        
        session = get_session()
        if session:
            category = session.query(Category).filter(Category.id == 1).first()
            if not category:
                from tests.factories.category_factory import CategoryFactory
                category = CategoryFactory.create()
            return category
        return None