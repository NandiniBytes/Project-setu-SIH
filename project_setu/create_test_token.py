from datetime import datetime, timedelta
from jose import jwt

# Configuration - must match security/auth.py
SECRET_KEY = "sih2025-super-secret-key"
ALGORITHM = "HS256"


def create_test_token():
    """
    Create a test JWT token for API authentication.
    
    Returns:
        JWT token string
    """
    # Set expiration time (24 hours from now)
    expire = datetime.utcnow() + timedelta(hours=24)
    
    # Create token payload
    payload = {
        "sub": "dr_aravind",  # Subject (user identifier)
        "exp": expire,         # Expiration time
        "iat": datetime.utcnow(),  # Issued at
        "iss": "project-setu",     # Issuer
        "aud": "api-users"         # Audience
    }
    
    # Generate JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return token


if __name__ == "__main__":
    # Generate and print the test token
    test_token = create_test_token()
    
    print("=" * 60)
    print("PROJECT SETU - TEST TOKEN GENERATOR")
    print("=" * 60)
    print(f"Generated JWT Token:")
    print(f"{test_token}")
    print("=" * 60)
    print("Usage:")
    print("curl -H 'Authorization: Bearer <token>' http://localhost:8000/api/CodeSystem/\$lookup")
    print("=" * 60)
    print("Token expires in 24 hours")
    print("=" * 60)
