from passlib.context import CryptContext

#Configuración de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    '''Hashea la contraseña usando bcrypt'''
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    '''Verifica si la contraseña es correcta'''
    return pwd_context.verify(plain_password, hashed_password)