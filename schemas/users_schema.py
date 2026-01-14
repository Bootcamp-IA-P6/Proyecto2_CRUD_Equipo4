from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from pydantic import ConfigDict


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str | None = None
    birth_date: date | None = None
    role_id: int

class UserOut(BaseModel):
    name: str
    email: EmailStr
    phone: str | None
    birth_date: date | None
    
    model_config = ConfigDict(from_attributes=True)
