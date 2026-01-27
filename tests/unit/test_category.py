
from controllers.category_controller import (
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category
)
from schemas.category_schemas import CategoryCreate, CategoryUpdate
from datetime import datetime, timezone
from tests.factories.category_factory import CategoryFactory
from fastapi_pagination import Params
from fastapi_pagination.api import set_params
from fastapi import HTTPException
import pytest


@pytest.fixture(autouse=True)
def setup_pagination():
    """Configura parámetros de paginación para cada test"""
    set_params(Params(page=1, size=50))
    yield



def test_create_category_success(db_session):
    """Test para crear una categoría exitosamente"""
   
    category_data = CategoryCreate(
        name="Educación",
        description="Proyectos educativos"
    )
    
    
    result = create_category(db_session, category_data)
    

    assert result.id is not None
    assert result.name == "Educación"
    assert result.description == "Proyectos educativos"


def test_create_category_duplicate_name(db_session):
    """Test crear categoría con nombre duplicado"""
   
    existing = CategoryFactory.create(name="Salud")
    
    category_data = CategoryCreate(
        name="Salud",
        description="Otra descripción"
    )
    
   
    with pytest.raises(HTTPException) as exc_info:
        create_category(db_session, category_data)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Category already exist"



def test_get_categories_success(db_session):
    """Test para obtener lista de categorías"""
   
    CategoryFactory.create_batch(5)
    
    
    result = get_categories(db_session)
    

    assert len(result.items) == 5
    assert result.total == 5


def test_get_categories_empty(db_session):
    """Test cuando no hay categorías"""
    result = get_categories(db_session)
    
    assert len(result.items) == 0
    assert result.total == 0


def test_get_categories_excludes_deleted(db_session):
    """Test que categorías eliminadas no aparecen"""
   
    active = CategoryFactory.create()
    deleted = CategoryFactory.create(deleted_at=datetime.now(timezone.utc))
    
    
    result = get_categories(db_session)
    

    assert len(result.items) == 1
    assert result.items[0].id == active.id


def test_get_category_success(db_session):
    """Test obtener categoría por ID"""
   
    category = CategoryFactory.create()
    
    
    result = get_category(db_session, category.id)
    

    assert result.id == category.id
    assert result.name == category.name


def test_get_category_not_found(db_session):
    """Test categoría no encontrada"""
   
    with pytest.raises(HTTPException) as exc_info:
        get_category(db_session, 999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Category not found"


def test_get_category_deleted(db_session):
    """Test categoría eliminada no se puede obtener"""
   
    deleted = CategoryFactory.create(deleted_at=datetime.now(timezone.utc))
    
   
    with pytest.raises(HTTPException) as exc_info:
        get_category(db_session, deleted.id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Category not found"



def test_update_category_success(db_session):
    """Test actualizar categoría exitosamente"""
   
    category = CategoryFactory.create(name="Original", description="Desc original")
    
    update_data = CategoryUpdate(
        name="Actualizado",
        description="Nueva descripción"
    )
    
    
    result = update_category(db_session, category.id, update_data)
    

    assert result.id == category.id
    assert result.name == "Actualizado"
    assert result.description == "Nueva descripción"


def test_update_category_partial(db_session):
    """Test actualización parcial"""
   
    category = CategoryFactory.create(name="Original", description="Desc original")
    
    update_data = CategoryUpdate(name="Solo nombre")
    
    
    result = update_category(db_session, category.id, update_data)
    

    assert result.name == "Solo nombre"
    assert result.description == "Desc original" 


def test_update_category_not_found(db_session):
    """Test actualizar categoría inexistente"""
   
    update_data = CategoryUpdate(name="Test")
    
   
    with pytest.raises(HTTPException) as exc_info:
        update_category(db_session, 999, update_data)
    
    assert exc_info.value.status_code == 404



def test_delete_category_success(db_session):
    """Test eliminar categoría (soft delete)"""
   
    category = CategoryFactory.create()
    
    
    result = delete_category(db_session, category.id)
    

    assert result.id == category.id
    assert result.deleted_at is not None


def test_delete_category_not_found(db_session):
    """Test eliminar categoría inexistente"""
   
    with pytest.raises(HTTPException) as exc_info:
        delete_category(db_session, 999)
    
    assert exc_info.value.status_code == 404


def test_delete_category_already_deleted(db_session):
    """Test eliminar categoría ya eliminada"""
   
    deleted = CategoryFactory.create(deleted_at=datetime.now(timezone.utc))
    
   
    with pytest.raises(HTTPException) as exc_info:
        delete_category(db_session, deleted.id)
    
    assert exc_info.value.status_code == 404 


def test_delete_category_and_verify_not_in_list(db_session):
    """Test que categoría eliminada no aparece en lista"""
   
    cat1 = CategoryFactory.create()
    cat2 = CategoryFactory.create()
    
    
    delete_category(db_session, cat1.id)
    

    result = get_categories(db_session)
    assert len(result.items) == 1
    assert result.items[0].id == cat2.id