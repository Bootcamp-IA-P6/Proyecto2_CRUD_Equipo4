from sqlalchemy.orm import Session
from models.role_model import Role
from schemas import role_schema as schema
from fastapi import HTTPException
from config.logging_config import get_logger


logger = get_logger("roles")


class RoleController:
    
    @staticmethod
    #GET ALL ROLES
    def get_roles(db: Session):
        logger.info("Getting roles list")
        return db.query(Role).all()
    
    @staticmethod
    #GET ROLE BY ID
    def get_one_role(db: Session, role_id: int):
        logger.info(f"Getting role with id={role_id}")
        return db.query(Role).filter(Role.id == role_id).first()
    
        if not role:
            logger.warning(f"Role with id={role_id} not found")
            raise HTTPException(status_code=404, detail="Role not found")
        return role
    
    @staticmethod
    #CREATE ROLE (futura escalabilidad)
    def create_role(db: Session, role: schema.RoleCreate):
        logger.info(f"Creating role with name={role.name}")
        
        try:
            db_role = Role(name=role.name)
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            logger.info(f"Role with id={db_role.id} created")
            return db_role
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Error creating role: {e}")
            raise HTTPException(status_code=500, detail="Error creating role")
        
        existing_role = db.query(Role).filter(Role.name == role.name).first()
        if existing_role:
            logger.warning(f"Role with name={role.name} already exists")
            raise HTTPException(status_code=400, detail="Role already exists")