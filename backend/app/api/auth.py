from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    decode_access_token,
    verify_token_type
)
from app.core.dependencies import get_current_user
from app.models.user import User, UserProfile
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - Validates email uniqueness
    - Validates email format
    - Hashes password with bcrypt
    - Creates user and empty profile
    
    Returns:
        UserResponse: Created user information
    
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Validate email format (additional check beyond Pydantic)
    if not user_data.email or '@' not in user_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        country=user_data.country,
        is_premium=False
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create empty user profile
        user_profile = UserProfile(
            user_id=new_user.id,
            skills=[],
            preferences={}
        )
        db.add(user_profile)
        db.commit()
        
        logger.info(f"New user registered: {new_user.email}")
        return new_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    
    - Validates email and password
    - Returns JWT access token
    
    Returns:
        Token: JWT access token and token type
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with user info
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "is_premium": user.is_premium
        }
    )
    
    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Returns:
        UserResponse: Current user information
    
    Requires:
        Valid JWT token in Authorization header
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh access token for authenticated user.
    
    Allows users to get a new access token without re-entering credentials.
    
    Returns:
        Token: New JWT access token
    
    Requires:
        Valid JWT token in Authorization header
    """
    # Create new access token
    access_token = create_access_token(
        data={
            "sub": str(current_user.id),
            "email": current_user.email,
            "is_premium": current_user.is_premium
        }
    )
    
    logger.info(f"Token refreshed for user: {current_user.email}")
    return {"access_token": access_token, "token_type": "bearer"}
