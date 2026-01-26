# tests/factories/volunteer_factory.py
from factory.declarations import LazyAttribute
from tests.factories.base_factory import BaseFactory
from models.volunteers_model import Volunteer
from domain.volunteer_enum import VolunteerStatus


class VolunteerFactory(BaseFactory):
    """Factory para crear voluntarios"""
    
    class Meta:
        model = Volunteer
    
    status = VolunteerStatus.active
    
    # 🔥 Usar LazyAttribute correctamente - solo obtener rol existente
    @LazyAttribute
    def user_id(self):
        """Crea usuario con rol existente"""
        from tests.factories.base_factory import get_session
        from tests.factories.user_factory import UserFactory
        from models.role_model import Role
        
        session = get_session()
        if session:
            # Intentar obtener rol existente en lugar de crearlo
            role = session.query(Role).filter(Role.id == 2).first()
            # No crear rol aquí, debe existir del test
            # Crear solo el usuario
            user = UserFactory.create()
            return user
        return None