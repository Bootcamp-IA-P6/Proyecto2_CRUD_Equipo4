# import pytest
# from database.database import Session
# from tests.factories.assignment_factory import AssignmentFactory
# from tests.factories.skill_factory import SkillFactory
# from tests.factories.project_skill_factory import ProjectSkillFactory
# from tests.factories.volunteer_skill_factory import VolunteerSkillFactory

# @pytest.fixture
# def db_session():
#     # Crea sesión temporal para test
#     session = Session()
#     yield session
#     session.rollback()
#     session.close()

# def test_assignment_factory_creates_valid_assignment(db_session):
#     # Creamos un skill primero
#     skill = SkillFactory()
#     db_session.flush()  # asegura que skill.id esté disponible

#     # Creamos project_skill y volunteer_skill usando factories
#     project_skill = ProjectSkillFactory(skill_id=skill.id)
#     volunteer_skill = VolunteerSkillFactory(skill_id=skill.id)
#     db_session.flush()  # asegura que tengan IDs

#     # Creamos el Assignment usando nuestra factory
#     assignment = AssignmentFactory(
#         project_skill_id=project_skill.id,
#         volunteer_skill_id=volunteer_skill.id
#     )

#     # Refrescamos para traer datos de la DB
#     db_session.refresh(assignment)

#     # Tests rápidos para comprobar que todo está bien
#     assert assignment.id is not None
#     assert assignment.project_skill_id == project_skill.id
#     assert assignment.volunteer_skill_id == volunteer_skill.id
#     assert assignment.status.name == "PENDING"

#     print("Assignment creado correctamente con IDs:", assignment.project_skill_id, assignment.volunteer_skill_id)
