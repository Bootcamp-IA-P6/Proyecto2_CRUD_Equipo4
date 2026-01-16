import datetime

from sqlalchemy.orm import Session
from schemas import project_schema as schema
from models.project_model import Project


class ProjectController:


    @staticmethod
    async def get_all_items(db: Session) -> list[schema.ProjectOut]:
        items = db.query(Project).all()
        return [schema.ProjectOut.model_validate(item) for item in items]

    @staticmethod
    async def get_items(db: Session, skip: int = 0, limit: int = 100) -> list[schema.ProjectOut]:
        items = db.query(Project).offset(skip).limit(limit).all()
        return [schema.ProjectOut.model_validate(item) for item in items]

    @staticmethod
    async def get_item(db: Session, item_id: int) -> schema.ProjectOut:
        item = db.query(Project).filter(Project.id == item_id).first()
        return schema.ProjectOut.model_validate(item) if item else None

    @staticmethod
    async def create_item(db: Session, item: schema.ProjectCreate)-> schema.ProjectOut:
        db_item = Project(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return schema.ProjectOut.model_validate(db_item)


    @staticmethod
    async def update_item(db: Session, item_id: int, item: schema.ProjectCreate) -> schema.ProjectOut:
        db_item = db.query(Project).filter(Project.id == item_id).first()
        if db_item:
            if item.name is not None:
                db_item.name = item.name
            if item.description is not None:
                db_item.description = item.description
            if item.deadline is not None:
                db_item.deadline = item.deadline
            if item.status is not None:
                db_item.status = item.status
            if item.priority is not None:
                db_item.priority = item.priority
            
            db.commit()
            db.refresh(db_item)
            return schema.ProjectOut.model_validate(db_item)
        return None


    @staticmethod
    async def delete_item(db: Session, item_id: int):
        db_item = db.query(Project).filter(Project.id == item_id).first()
        if db_item:
            db.delete(db_item)
            db.commit()
        return None