# tests/factories/base_factory.py
import factory
from sqlalchemy.orm import Session as SessionType


# Variable global para almacenar la sesión compartida
_session = None


def set_factory_session(session):
    """Configura la sesión para todas las factories"""
    global _session
    _session = session


def get_factory_session():
    """Obtiene la sesión actual"""
    return _session


def get_session():
    """Obtiene la sesión actual (alias para compatibilidad)"""
    return _session


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Factory base para todos los modelos SQLAlchemy.
    Todos los factories deben heredar de esta clase.
    """
    
    class Meta:
        abstract = True
        sqlalchemy_session_factory = get_factory_session  # Usa función para obtener sesión
        sqlalchemy_session_persistence = "flush"


# Alias para mantener compatibilidad 
SQLAlchemyFactory = BaseFactory