from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class Doctor(Base):
    """
    SQLAlchemy model for Doctor users.
    
    Represents medical professionals with authentication and profile information.
    """
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    medical_license_number = Column(String, unique=True, nullable=False)
    specialty = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Doctor(id={self.id}, email='{self.email}', specialty='{self.specialty}')>"
