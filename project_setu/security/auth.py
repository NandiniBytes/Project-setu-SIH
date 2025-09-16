from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

# Configuration
SECRET_KEY = "sih2025-super-secret-key"
ALGORITHM = "HS256"
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token from Authorization header.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid, malformed, or expired
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=401,
                detail="Token missing expiration claim"
            )
        
        # Convert exp timestamp to datetime for comparison
        exp_datetime = datetime.fromtimestamp(exp)
        if exp_datetime < datetime.utcnow():
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}"
        )
