from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its hash.
    
    Args:
        plain_password: The plaintext password to verify
        hashed_password: The hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password.
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def get_doctor_by_email(db: Session, email: str) -> models.Doctor:
    """
    Fetch a doctor from the database by email.
    
    Args:
        db: Database session
        email: Doctor's email address
        
    Returns:
        Doctor model instance or None if not found
    """
    return db.query(models.Doctor).filter(models.Doctor.email == email).first()


def get_doctor_by_license(db: Session, license_number: str) -> models.Doctor:
    """
    Fetch a doctor from the database by medical license number.
    
    Args:
        db: Database session
        license_number: Medical license number
        
    Returns:
        Doctor model instance or None if not found
    """
    return db.query(models.Doctor).filter(
        models.Doctor.medical_license_number == license_number
    ).first()


def create_doctor(db: Session, doctor: schemas.DoctorCreate) -> models.Doctor:
    """
    Create a new doctor in the database with hashed password.
    
    Args:
        db: Database session
        doctor: DoctorCreate schema with doctor data
        
    Returns:
        Created Doctor model instance
    """
    # Hash the password
    hashed_password = get_password_hash(doctor.password)
    
    # Create doctor instance
    db_doctor = models.Doctor(
        full_name=doctor.full_name,
        email=doctor.email,
        hashed_password=hashed_password,
        medical_license_number=doctor.medical_license_number,
        specialty=doctor.specialty
    )
    
    # Add to database
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    
    return db_doctor


def authenticate_doctor(db: Session, email: str, password: str) -> models.Doctor:
    """
    Authenticate a doctor by email and password.
    
    Args:
        db: Database session
        email: Doctor's email address
        password: Plaintext password
        
    Returns:
        Doctor model instance if authentication successful, None otherwise
    """
    doctor = get_doctor_by_email(db, email)
    if not doctor:
        return None
    if not verify_password(password, doctor.hashed_password):
        return None
    return doctor
