from sqlalchemy.orm import Session
from models.role_model import Role
from schemas import role_schema

class RoleController:
    
    @staticmethod
    #GET ALL ROLES
    async def get_roles(db: Session):
        return db.query(Role).all()
    
    @staticmethod
    #GET ROLE BY ID
    async def get_one_role(db: Session, role_id: int):
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    #CREATE ROLE (futura escalabilidad)
    async def create_role(db: Session, role: role_schema.RoleCreate):
        role = Role(name=role.name)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role