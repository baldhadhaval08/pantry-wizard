"""User authentication and profile routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.models import User
from app.schemas import UserRegister, UserLogin, Token, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, session: Session = Depends(get_session)):
    """
    Register a new user.
    
    Creates a new user account with health profile information.
    Returns JWT token for authentication.
    """
    # Check if user already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        height_cm=user_data.height_cm,
        weight_kg=user_data.weight_kg,
        age=user_data.age,
        diet_type=user_data.diet_type,
        allergies=user_data.allergies,
        goal=user_data.goal
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, session: Session = Depends(get_session)):
    """
    Login user and return JWT token.
    
    Authenticates user with email and password, returns JWT token.
    """
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    
    Returns the authenticated user's profile information.
    """
    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        height_cm=current_user.height_cm,
        weight_kg=current_user.weight_kg,
        age=current_user.age,
        diet_type=current_user.diet_type,
        allergies=current_user.allergies,
        goal=current_user.goal,
        created_at=current_user.created_at
    )

