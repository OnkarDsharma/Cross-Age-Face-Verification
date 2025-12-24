from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..config import settings
from ..schemas import TokenData
from ..database import get_user_by_username
from ..models import UserInDB
import logging


logger = logging.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        # Truncate password to 72 bytes (bcrypt limitation)
        if len(plain_password) > 72:
            plain_password = plain_password[:72]
            logger.warning("Password truncated to 72 bytes for bcrypt")
        
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        # Truncate password to 72 bytes (bcrypt limitation)
        if len(password) > 72:
            password = password[:72]
            logger.warning("Password truncated to 72 bytes for bcrypt")
        
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


async def authenticate_user(username: str, password: str):
    """Authenticate a user"""
    try:
        user = await get_user_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            return False
        
        # Convert dict to object-like structure if needed
        if isinstance(user, dict):
            class UserObj:
                def __init__(self, data):
                    self.password_hash = data.get('password_hash')
                    self.__dict__.update(data)
            user = UserObj(user)
        
        if not verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {username}")
            return False
        
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return False


async def get_current_user(token: str):
    """Get current user from JWT token"""
    from fastapi import HTTPException, status
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(username)
    
    if user is None:
        raise credentials_exception
    
    return user
