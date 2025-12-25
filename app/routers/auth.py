from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas.user import UserLogin, Token, RefreshToken, UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only admin can create users
):
    """Register a new user (Admin only)"""
    try:
        # Additional validation for password length
        if len(user.password) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is too long. Maximum 72 characters allowed."
            )
        
        # Convert role string to enum if needed
        if isinstance(user.role, str):
            if user.role.upper() == "ADMIN":
                user.role = UserRole.ADMIN
            else:
                user.role = UserRole.ORDER_MAINTAINER
        
        db_user = UserService.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login user and return JWT tokens"""
    from app.models.user import User
    import hashlib
    from app.core.auth import verify_password
    
    user = db.query(User).filter(User.username == user_credentials.username).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Try both hash methods (bcrypt and simple hash for compatibility)
    password_valid = False
    
    try:
        # First try bcrypt (for properly created users)
        password_valid = verify_password(user_credentials.password, user.hashed_password)
    except:
        # If bcrypt fails, try simple hash (for admin user created via create-first-admin)
        simple_hash = hashlib.sha256(user_credentials.password.encode()).hexdigest()
        password_valid = (user.hashed_password == simple_hash)
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token_expires = timedelta(minutes=30)  # 30 minutes
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    
    # Set refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Use HTTPS in production
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_data: RefreshToken, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        payload = verify_token(refresh_data.refresh_token, "refresh")
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        user = UserService.get_user(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token
        new_refresh_token = create_refresh_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing refresh token cookie"""
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/users", response_model=list[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users (Admin only)"""
    return UserService.get_users(db, skip=skip, limit=limit)


@router.post("/create-first-admin")
def create_first_admin(db: Session = Depends(get_db)):
    """Create first admin user - public endpoint for initial setup"""
    try:
        # Check if ANY user exists
        from app.models.user import User, UserRole
        existing_users = db.query(User).count()
        if existing_users > 0:
            return {"message": "Users already exist. Use /init-admin instead."}
        
        # Create admin user with minimal validation
        import hashlib
        
        # Use simple hash instead of bcrypt for initial setup
        simple_password = "admin"
        password_hash = hashlib.sha256(simple_password.encode()).hexdigest()
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=password_hash,  # Simple hash for now
            full_name="Admin",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        return {
            "message": "First admin created successfully",
            "username": "admin",
            "password": "admin",
            "note": "Login and create proper users through the interface"
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}


@router.post("/quick-login")
def quick_login(username: str, password: str, db: Session = Depends(get_db)):
    """Quick login for simple hash users"""
    try:
        from app.models.user import User
        import hashlib
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Check simple hash
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.hashed_password != password_hash:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Create tokens
        from app.core.auth import create_access_token, create_refresh_token
        from datetime import timedelta
        
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role},
            expires_delta=timedelta(minutes=30)
        )
        
        refresh_token = create_refresh_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))