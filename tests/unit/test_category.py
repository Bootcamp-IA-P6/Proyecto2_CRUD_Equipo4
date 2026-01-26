# import pytest
# from fastapi import HTTPException

# from controllers.category_controller import (
#     create_category,
#     get_categories,
#     get_category,
#     update_category,
#     delete_category
# )

# from schemas.category_schemas import CategoryCreate, CategoryUpdate
# from models.category_model import Category


# # create
# def test_create_category_success(db_session):
#     data = CategoryCreate(
#         name="Educación",
#         description="Categoría educativa"
#     )

#     category = create_category(db_session, data)

#     assert category.id is not None
#     assert category.name == "Educación"
#     assert category.description == "Categoría educativa"
#     assert category.deleted_at is None

#     saved = db_session.query(Category).first()
#     assert saved is not None


# def test_create_category_duplicate_name(db_session):
#     data = CategoryCreate(
#         name="Salud",
#         description="Primera"
#     )

#     create_category(db_session, data)

#     with pytest.raises(HTTPException) as exc:
#         create_category(db_session, data)

#     assert exc.value.status_code == 400


# # get

# def test_get_categories_returns_list(db_session):
#     create_category(
#         db_session,
#         CategoryCreate(name="A", description="desc A")
#     )
#     create_category(
#         db_session,
#         CategoryCreate(name="B", description="desc B")
#     )

#     categories = get_categories(db_session)

#     assert len(categories) == 2


# # get_id

# def test_get_category_by_id(db_session):
#     category = create_category(
#         db_session,
#         CategoryCreate(name="Tech", description="Tech desc")
#     )

#     result = get_category(db_session, category.id)

#     assert result.id == category.id
#     assert result.name == "Tech"


# def test_get_category_not_found(db_session):
#     with pytest.raises(HTTPException) as exc:
#         get_category(db_session, 999)

#     assert exc.value.status_code == 404


# # update

# def test_update_category_success(db_session):
#     category = create_category(
#         db_session,
#         CategoryCreate(name="Old", description="Old desc")
#     )

#     data = CategoryUpdate(
#         name="New",
#         description="New desc"
#     )

#     updated = update_category(db_session, category.id, data)

#     assert updated.name == "New"
#     assert updated.description == "New desc"


# # delete

# def test_delete_category_soft(db_session):
#     category = create_category(
#         db_session,
#         CategoryCreate(name="Eliminar", description="desc")
#     )

#     deleted = delete_category(db_session, category.id)

#     assert deleted.deleted_at is not None


# def test_deleted_category_not_returned(db_session):
#     category = create_category(
#         db_session,
#         CategoryCreate(name="Invisible", description="desc")
#     )

#     delete_category(db_session, category.id)

#     categories = get_categories(db_session)
#     assert len(categories) == 0
