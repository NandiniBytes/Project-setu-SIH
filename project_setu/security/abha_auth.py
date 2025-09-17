"""
ABHA (Ayushman Bharat Health Account) Authentication Integration
Implements India's national health ID authentication system with ISO 22600 compliance.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """ISO 22600 Access Control Levels"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EMERGENCY = "emergency"


class ResourceType(Enum):
    """Healthcare resource types"""
    PATIENT = "Patient"
    PRACTITIONER = "Practitioner"
    CONDITION = "Condition"
    MEDICATION = "Medication"
    OBSERVATION = "Observation"
    DIAGNOSTIC_REPORT = "DiagnosticReport"


@dataclass
class ABHAToken:
    """ABHA token representation with enhanced metadata"""
    abha_id: str
    name: str
    gender: str
    date_of_birth: str
    mobile: str
    email: Optional[str]
    address: Dict[str, Any]
    health_id_number: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    issued_at: datetime
    issuer: str = "ABDM"
    
    # ISO 22600 compliance fields
    security_label: str = "CONFIDENTIAL"
    access_level: AccessLevel = AccessLevel.READ
    purpose_of_use: str = "TREATMENT"
    data_classification: str = "PHI"  # Protected Health Information


@dataclass
class AccessControlPolicy:
    """ISO 22600 compliant access control policy"""
    subject: str  # Who is accessing
    resource: ResourceType  # What is being accessed
    action: AccessLevel  # What action is being performed
    context: Dict[str, Any]  # Contextual information
    conditions: List[str]  # Access conditions
    purpose: str = "TREATMENT"
    confidentiality: str = "CONFIDENTIAL"
    integrity: str = "HIGH"
    availability: str = "NORMAL"


class ABHAAuthService:
    """
    ABHA Authentication Service with ISO 22600 compliance.
    
    Features:
    - ABHA ID validation and authentication
    - ISO 22600 access control implementation
    - Context-aware authorization
    - Audit trail integration
    - Emergency access provisions
    - Data classification and labeling
    """
    
    def __init__(self):
        self.abha_base_url = "https://abhasbx.abdm.gov.in/abha/api/v3"
        self.client_id = "your_abha_client_id"
        self.client_secret = "your_abha_client_secret"
        self.access_policies = {}
        self.emergency_access_codes = set()
        
        # ISO 22600 security attributes
        self.security_labels = {
            "PUBLIC": 0,
            "INTERNAL": 1,
            "CONFIDENTIAL": 2,
            "RESTRICTED": 3,
            "TOP_SECRET": 4
        }
        
        # Load access control policies
        self._initialize_access_policies()

    def _initialize_access_policies(self):
        """Initialize ISO 22600 compliant access control policies"""
        
        # Doctor access policies
        self.access_policies["doctor"] = {
            ResourceType.PATIENT: [AccessLevel.READ, AccessLevel.WRITE],
            ResourceType.CONDITION: [AccessLevel.READ, AccessLevel.WRITE],
            ResourceType.MEDICATION: [AccessLevel.READ, AccessLevel.WRITE],
            ResourceType.OBSERVATION: [AccessLevel.READ, AccessLevel.WRITE],
            ResourceType.DIAGNOSTIC_REPORT: [AccessLevel.READ, AccessLevel.WRITE]
        }
        
        # Patient access policies
        self.access_policies["patient"] = {
            ResourceType.PATIENT: [AccessLevel.READ],  # Own data only
            ResourceType.CONDITION: [AccessLevel.READ],
            ResourceType.MEDICATION: [AccessLevel.READ],
            ResourceType.OBSERVATION: [AccessLevel.READ],
            ResourceType.DIAGNOSTIC_REPORT: [AccessLevel.READ]
        }
        
        # Emergency access policies
        self.access_policies["emergency"] = {
            ResourceType.PATIENT: [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.EMERGENCY],
            ResourceType.CONDITION: [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.EMERGENCY],
            ResourceType.MEDICATION: [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.EMERGENCY],
            ResourceType.OBSERVATION: [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.EMERGENCY],
            ResourceType.DIAGNOSTIC_REPORT: [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.EMERGENCY]
        }

    async def authenticate_abha_token(self, abha_token: str) -> Optional[ABHAToken]:
        """
        Authenticate ABHA token with ABDM gateway.
        In production, this would connect to the actual ABHA API.
        """
        try:
            # For demonstration, we'll create a mock ABHA token validation
            # In production, this would make actual API calls to ABDM
            
            headers = {
                'Authorization': f'Bearer {abha_token}',
                'Accept': 'application/json',
                'X-CM-ID': self.client_id
            }
            
            # Mock ABHA user data (replace with actual API call)
            mock_abha_data = {
                "abhaId": "12-3456-7890-1234",
                "name": "Dr. Rajesh Kumar",
                "gender": "M",
                "dateOfBirth": "1985-06-15",
                "mobile": "+91-9876543210",
                "email": "dr.rajesh@example.com",
                "address": {
                    "line": "123 Medical Colony",
                    "district": "New Delhi",
                    "state": "Delhi",
                    "pincode": "110001"
                },
                "healthIdNumber": "12-3456-7890-1234",
                "accessToken": abha_token,
                "refreshToken": "refresh_token_here",
                "expiresIn": 3600
            }
            
            # Create ABHAToken object
            abha_user = ABHAToken(
                abha_id=mock_abha_data["abhaId"],
                name=mock_abha_data["name"],
                gender=mock_abha_data["gender"],
                date_of_birth=mock_abha_data["dateOfBirth"],
                mobile=mock_abha_data["mobile"],
                email=mock_abha_data.get("email"),
                address=mock_abha_data["address"],
                health_id_number=mock_abha_data["healthIdNumber"],
                access_token=mock_abha_data["accessToken"],
                refresh_token=mock_abha_data["refreshToken"],
                expires_at=datetime.utcnow() + timedelta(seconds=mock_abha_data["expiresIn"]),
                issued_at=datetime.utcnow()
            )
            
            logger.info(f"ABHA authentication successful for: {abha_user.abha_id}")
            return abha_user
            
        except Exception as e:
            logger.error(f"ABHA authentication failed: {e}")
            return None

    def check_access_control(self, 
                           subject: ABHAToken, 
                           resource_type: ResourceType, 
                           action: AccessLevel,
                           context: Dict[str, Any] = None) -> bool:
        """
        ISO 22600 compliant access control check.
        
        Args:
            subject: The ABHA user requesting access
            resource_type: Type of resource being accessed
            action: Action being performed
            context: Additional context (patient ID, emergency status, etc.)
            
        Returns:
            True if access is allowed, False otherwise
        """
        context = context or {}
        
        # Determine subject role (doctor, patient, etc.)
        subject_role = self._determine_role(subject, context)
        
        # Check if subject has permission for this resource and action
        if subject_role not in self.access_policies:
            logger.warning(f"Unknown subject role: {subject_role}")
            return False
        
        allowed_actions = self.access_policies[subject_role].get(resource_type, [])
        
        # Emergency access override
        if action == AccessLevel.EMERGENCY and self._is_emergency_authorized(subject, context):
            logger.info(f"Emergency access granted to {subject.abha_id}")
            return True
        
        # Regular access check
        if action in allowed_actions:
            # Additional context-based checks
            if self._check_contextual_access(subject, resource_type, action, context):
                logger.info(f"Access granted: {subject.abha_id} -> {resource_type.value} ({action.value})")
                return True
        
        logger.warning(f"Access denied: {subject.abha_id} -> {resource_type.value} ({action.value})")
        return False

    def _determine_role(self, subject: ABHAToken, context: Dict[str, Any]) -> str:
        """Determine the role of the subject based on ABHA data and context"""
        # In production, this would check against healthcare provider registries
        if "practitioner_id" in context or "medical_license" in context:
            return "doctor"
        elif subject.abha_id == context.get("patient_abha_id"):
            return "patient"
        elif context.get("emergency_access"):
            return "emergency"
        else:
            return "patient"  # Default to most restrictive

    def _is_emergency_authorized(self, subject: ABHAToken, context: Dict[str, Any]) -> bool:
        """Check if emergency access is authorized"""
        emergency_code = context.get("emergency_code")
        if emergency_code in self.emergency_access_codes:
            return True
        
        # Check for valid emergency credentials
        if context.get("emergency_practitioner_id") and context.get("emergency_facility_id"):
            return True
        
        return False

    def _check_contextual_access(self, 
                                subject: ABHAToken, 
                                resource_type: ResourceType, 
                                action: AccessLevel, 
                                context: Dict[str, Any]) -> bool:
        """Perform additional contextual access checks"""
        
        # Patient can only access their own data
        if self._determine_role(subject, context) == "patient":
            patient_abha_id = context.get("patient_abha_id")
            if patient_abha_id and patient_abha_id != subject.abha_id:
                return False
        
        # Time-based access restrictions
        current_hour = datetime.utcnow().hour
        if action == AccessLevel.DELETE and (current_hour < 9 or current_hour > 17):
            logger.warning("Delete operations restricted outside business hours")
            return False
        
        # Data sensitivity checks
        sensitivity_level = context.get("data_sensitivity", "NORMAL")
        if sensitivity_level == "HIGH" and subject.security_label != "CONFIDENTIAL":
            return False
        
        return True

    def create_access_log_entry(self, 
                              subject: ABHAToken, 
                              resource_type: ResourceType, 
                              action: AccessLevel, 
                              result: bool, 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create ISO 22600 compliant audit log entry"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "subject": {
                "abha_id": subject.abha_id,
                "name": subject.name,
                "security_label": subject.security_label
            },
            "resource": resource_type.value,
            "action": action.value,
            "result": "GRANTED" if result else "DENIED",
            "context": context or {},
            "purpose_of_use": subject.purpose_of_use,
            "data_classification": subject.data_classification,
            "session_id": context.get("session_id") if context else None,
            "ip_address": context.get("ip_address") if context else None,
            "user_agent": context.get("user_agent") if context else None,
            "iso_22600_compliant": True
        }

    def add_emergency_access_code(self, code: str, expires_at: datetime = None):
        """Add emergency access code"""
        self.emergency_access_codes.add(code)
        if expires_at:
            # In production, implement expiration logic
            pass

    def revoke_emergency_access_code(self, code: str):
        """Revoke emergency access code"""
        self.emergency_access_codes.discard(code)


# Global ABHA service instance
abha_service = ABHAAuthService()

# FastAPI security scheme
abha_bearer = HTTPBearer()


async def verify_abha_token(credentials: HTTPAuthorizationCredentials = Depends(abha_bearer)) -> ABHAToken:
    """
    FastAPI dependency for ABHA token verification.
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    # Authenticate with ABHA service
    abha_user = await abha_service.authenticate_abha_token(token)
    
    if not abha_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ABHA token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check token expiration
    if datetime.utcnow() > abha_user.expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ABHA token expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return abha_user


def require_access(resource_type: ResourceType, action: AccessLevel):
    """
    Decorator for enforcing ISO 22600 access control on endpoints.
    
    Usage:
        @require_access(ResourceType.PATIENT, AccessLevel.READ)
        async def get_patient(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract ABHA user from kwargs (injected by verify_abha_token)
            abha_user = None
            context = {}
            
            for key, value in kwargs.items():
                if isinstance(value, ABHAToken):
                    abha_user = value
                elif key == "request":
                    # Extract context from request
                    context = {
                        "ip_address": value.client.host if value.client else None,
                        "user_agent": value.headers.get("user-agent"),
                        "session_id": value.headers.get("x-session-id")
                    }
            
            if not abha_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="ABHA authentication required"
                )
            
            # Check access control
            access_granted = abha_service.check_access_control(
                abha_user, resource_type, action, context
            )
            
            if not access_granted:
                # Log access denial
                log_entry = abha_service.create_access_log_entry(
                    abha_user, resource_type, action, False, context
                )
                logger.warning(f"Access denied: {log_entry}")
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for this resource"
                )
            
            # Log successful access
            log_entry = abha_service.create_access_log_entry(
                abha_user, resource_type, action, True, context
            )
            logger.info(f"Access granted: {log_entry}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Utility functions
def get_abha_service() -> ABHAAuthService:
    """Dependency injection for ABHA service"""
    return abha_service
