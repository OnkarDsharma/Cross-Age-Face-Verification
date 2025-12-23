from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas import Token, LoginRequest
from ..models import UserCreate, UserResponse
from ..database import user_exists, create_user
from .utils import authenticate_user, create_access_token, get_current_user, get_password_hash
from ..config import settings
from ..models import UserInDB

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    if await user_exists(email=user.email) or await user_exists(username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create user
    password_hash = get_password_hash(user.password)
    new_user = await create_user(user.email, user.username, password_hash)
    
    return UserResponse(
        _id=str(new_user.id),
        email=new_user.email,
        username=new_user.username,
        created_at=new_user.created_at
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token (OAuth2 compatible)"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        _id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        created_at=current_user.created_at
    )