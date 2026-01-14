import datetime

from sqlalchemy.orm import Session
from schemas import project_schema as schema
from models.project_model import Project


class ProjectController:


    @staticmethod
    async def get_all_items(db: Session):
        return db.query(Project).all()

    @staticmethod
    async def get_items(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Project).offset(skip).limit(limit).all()

    @staticmethod
    async def get_item(db: Session, item_id: int):
        return db.query(Project).filter(Project.id == item_id).first()


    @staticmethod
    async def create_item(db: Session, item: schema.ProjectCreate):
        db_item = Project(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item


    @staticmethod
    async def update_item(db: Session, item_id: int, item: schema.ProjectCreate):
        db_item = db.query(Project).filter(Project.id == item_id).first()
        if db_item:
            db_item.name = item.name
            db_item.description = item.description
            db_item.deadline= item.deadline
            db_item.status=item.status
            db_item.priority= item.priority
            #db_item.category_id= item.category_id
            db.commit()
            db.refresh(db_item)
        return db_item


    @staticmethod
    async def delete_item(db: Session, item_id: int):
        db_item = db.query(Project).filter(Project.id == item_id).first()
        if db_item:
            db.delete(db_item)
            db.commit()
        return db_item