import factory
from factory.alchemy import SQLAlchemyModelFactory
from app.models.assignment_model import Assignment
from app.tests.factories.project_skill_factory import ProjectSkillFactory
from app.tests.factories.volunteer_skill_factory import VolunteerSkillFactory
from app.database.database import Session
from app.domain.assignment_enum import AssignmentStatus

db_session = Session()

class AssignmentFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Assignment
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = "flush"


    project_skill_id = factory.SelfAttribute("project_skill.id")
    volunteer_skill_id = factory.SelfAttribute("volunteer_skill.id")

 
    project_skill = factory.SubFactory(ProjectSkillFactory)
    volunteer_skill = factory.SubFactory(VolunteerSkillFactory)

    status = AssignmentStatus.PENDING
