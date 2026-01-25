from pydantic import BaseModel, ConfigDict

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleOut(RoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

