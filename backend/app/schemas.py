from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    email: str
    username: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class VerificationRequest(BaseModel):
    pass  # Images come via FormData

class VerificationResponse(BaseModel):
    result: str
    message: str
    confidence_score: float
    distance: float

class VerificationHistory(BaseModel):
    id: str
    user_id: str
    result: str
    confidence_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class VerificationResult(BaseModel):
    result: str
    confidence_score: float
    message: str
    verification_id: str