from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from pydantic import ConfigDict
from typing import Optional


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
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    #role_id: Optional[int] = None solo si se podra cambiar de rol 
    
    model_config = ConfigDict(from_attributes=True)
