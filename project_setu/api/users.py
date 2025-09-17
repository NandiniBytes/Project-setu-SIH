from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt

import crud
import schemas
from database import get_db
from security.auth import SECRET_KEY, ALGORITHM, verify_token

router = APIRouter()


def create_access_token(data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/doctors/register", response_model=schemas.Doctor)
async def register_doctor(
    doctor: schemas.DoctorCreate,
    db: Session = Depends(get_db)
) -> schemas.Doctor:
    """
    Register a new doctor.
    
    Args:
        doctor: Doctor registration data
        db: Database session
        
    Returns:
        Created doctor data (without password)
        
    Raises:
        HTTPException: If email or license number already exists
    """
    # Check if email already exists
    db_doctor_email = crud.get_doctor_by_email(db, email=doctor.email)
    if db_doctor_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if medical license number already exists
    db_doctor_license = crud.get_doctor_by_license(db, license_number=doctor.medical_license_number)
    if db_doctor_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical license number already registered"
        )
    
    # Create new doctor
    created_doctor = crud.create_doctor(db=db, doctor=doctor)
    return created_doctor


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> schemas.Token:
    """
    Login endpoint to get access token.
    
    Args:
        form_data: OAuth2 form data with username (email) and password
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate doctor (username is email in OAuth2PasswordRequestForm)
    doctor = crud.authenticate_doctor(db, email=form_data.username, password=form_data.password)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if doctor account is active
    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={
            "sub": doctor.email,
            "doctor_id": doctor.id,
            "full_name": doctor.full_name,
            "specialty": doctor.specialty
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/doctors/me", response_model=schemas.Doctor)
async def get_current_doctor(
    token_payload: Dict[str, Any] = Depends(verify_token),
    db: Session = Depends(get_db)
) -> schemas.Doctor:
    """
    Get current doctor's profile information.
    
    Args:
        db: Database session
        token_payload: Decoded JWT token payload
        
    Returns:
        Current doctor's profile data
        
    Raises:
        HTTPException: If doctor not found
    """
    
    doctor_email = token_payload.get("sub")
    if not doctor_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    doctor = crud.get_doctor_by_email(db, email=doctor_email)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    return doctor
