from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


#Para el registro
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    
#para el login 
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
#para devolver token JWT
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
#Informacion del usuario dentro del token
class TokenData(BaseModel):
    id: int | None = None
    email: str | None = None
    role_id: int | None = None
