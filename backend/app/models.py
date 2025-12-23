from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from datetime import datetime
from bson import ObjectId
from typing import Any


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    username: str
    password: str


class UserInDB(BaseModel):
    """Schema for user in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: Any = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_serializer('id')
    def serialize_id(self, value: Any, _info):
        return str(value)


class UserResponse(BaseModel):
    """Schema for user response (public data)"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(alias="_id")
    email: EmailStr
    username: str
    created_at: datetime


class VerificationInDB(BaseModel):
    """Schema for verification record in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: Any = Field(default_factory=ObjectId, alias="_id")
    user_id: str
    image1_filename: str
    image2_filename: str
    result: str
    confidence_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_serializer('id')
    def serialize_id(self, value: Any, _info):
        return str(value)


class VerificationResponse(BaseModel):
    """Schema for verification response"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(alias="_id")
    result: str
    confidence_score: float
    image1_filename: str
    image2_filename: str
    created_at: datetime