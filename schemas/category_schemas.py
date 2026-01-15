from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    description: str = None

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase): 
    id: int

    class Config:
        orm_mode = True 