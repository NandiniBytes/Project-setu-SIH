from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class DoctorCreate(BaseModel):
    """
    Pydantic schema for doctor registration.
    
    Used when creating a new doctor account.
    """
    full_name: str = Field(..., min_length=2, max_length=100, description="Doctor's full name")
    email: EmailStr = Field(..., description="Doctor's email address")
    password: str = Field(..., min_length=8, description="Password (plaintext, will be hashed)")
    medical_license_number: str = Field(..., min_length=5, max_length=50, description="Medical license number")
    specialty: str = Field(..., min_length=2, max_length=100, description="Medical specialty")


class Doctor(BaseModel):
    """
    Pydantic schema for returning doctor data.
    
    Used when returning doctor information (excludes hashed_password).
    """
    id: int
    full_name: str
    email: str
    medical_license_number: str
    specialty: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility with SQLAlchemy


class Token(BaseModel):
    """
    Pydantic schema for JWT token response.
    
    Used when returning authentication tokens.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Pydantic schema for token payload data.
    
    Used for token validation and user identification.
    """
    email: Optional[str] = None
