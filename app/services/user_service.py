from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.auth import get_password_hash, verify_password


class UserService:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user"""
        # Check if username already exists
        if UserService.get_user_by_username(db, user.username):
            raise ValueError(f"Username '{user.username}' already exists")
        
        # Check if email already exists
        if UserService.get_user_by_email(db, user.email):
            raise ValueError(f"Email '{user.email}' already exists")
        
        # Create user (no password length restriction with scrypt)
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user"""
        user = UserService.get_user(db, user_id)
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> bool:
        """Deactivate user"""
        user = UserService.get_user(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        db.commit()
        return True

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users"""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create_default_admin(db: Session) -> User:
        """Create default admin user if none exists"""
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin:
            return admin
        
        # Use a simple password that works with bcrypt
        admin_user = UserCreate(
            username="admin",
            email="admin@foodinventory.com",
            password="admin",  # Simple password for initial setup
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        
        return UserService.create_user(db, admin_user)