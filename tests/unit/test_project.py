import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta

from controllers.project_controller import ProjectController
from schemas.project_schema import ProjectCreate
from schemas.category_schemas import CategoryCreate
from models.project_model import Project
from controllers.category_controller import create_category


@pytest.mark.asyncio
async def test_create_project_success(db_session):
    category = create_category(
        db_session,
        CategoryCreate(
            name="Categoria Test",
            description="desc"
        )
    )

    data = ProjectCreate(
        name="Proyecto A",
        description="Proyecto de prueba",
        deadline=datetime.utcnow() + timedelta(days=10),
        status="assigned",
        priority="high",
        category_id=category.id
    )

    await ProjectController.create_item(db_session, data)

    saved = db_session.query(Project).first()
    assert saved is not None
    assert saved.name == "Proyecto A"
    assert saved.category_id == category.id


@pytest.mark.asyncio
async def test_create_project_duplicate_name(db_session):
    category = create_category(
        db_session,
        CategoryCreate(name="Cat Dup", description="desc")
    )

    data = ProjectCreate(
        name="Proyecto Duplicado",
        description="desc",
        deadline=datetime.utcnow(),
        status="assigned",
        priority="medium",
        category_id=category.id
    )

    await ProjectController.create_item(db_session, data)

    with pytest.raises(HTTPException) as exc:
        await ProjectController.create_item(db_session, data)

    assert exc.value.status_code == 400
