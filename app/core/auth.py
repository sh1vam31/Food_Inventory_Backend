from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings
import hashlib
import secrets
import base64


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using multiple methods"""
    try:
        # Method 1: Try scrypt hash (new method)
        if ':' in hashed_password and len(hashed_password.split(':')) == 2:
            salt, stored_hash = hashed_password.split(':')
            salt_bytes = base64.b64decode(salt)
            computed_hash = hashlib.scrypt(
                plain_password.encode('utf-8'), 
                salt=salt_bytes, 
                n=16384, r=8, p=1, 
                dklen=32
            )
            return base64.b64encode(computed_hash).decode('utf-8') == stored_hash
        
        # Method 2: Try simple SHA256 hash (for admin user)
        simple_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        if hashed_password == simple_hash:
            return True
            
        # Method 3: Try bcrypt (for backward compatibility)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
        
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using scrypt (no length limitations)"""
    # Generate a random salt
    salt = secrets.token_bytes(32)
    
    # Hash the password using scrypt
    hashed = hashlib.scrypt(
        password.encode('utf-8'), 
        salt=salt, 
        n=16384, r=8, p=1, 
        dklen=32
    )
    
    # Return salt:hash format
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    hash_b64 = base64.b64encode(hashed).decode('utf-8')
    return f"{salt_b64}:{hash_b64}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )