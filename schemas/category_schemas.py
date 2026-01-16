from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str
    description: str|None

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase): 
    id: int

    model_config = ConfigDict(from_attributes=True)