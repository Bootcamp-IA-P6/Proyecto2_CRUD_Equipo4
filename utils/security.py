from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

from dotenv import load_dotenv
import os

load_dotenv()

#Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", 7))


#Configuración de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Contraseñas
def hash_password(password: str) -> str:
    '''Hashea la contraseña usando bcrypt'''
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    '''Verifica si la contraseña es correcta'''
    return pwd_context.verify(plain_password, hashed_password)

#JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    '''Crea un token JWT'''
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    '''Decodifica un token JWT'''
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None