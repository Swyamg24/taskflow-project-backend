from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserResponse, UserLogin, Token
from app.crud import user_crud
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user, require_admin
from app.models import User

# APIRouter = FastAPI's version of Express Router
# prefix = all routes here start with /auth
# tags = groups routes in Swagger UI
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    - Pydantic auto-validates the request body
    - response_model=UserResponse means FastAPI auto-filters the response
      (removes hashed_password field automatically)
    """
    # Check if email already exists
    existing = user_crud.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    user = user_crud.create_user(db, user_data)
    return user   # FastAPI serializes using UserResponse schema


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and receive JWT token.
    """
    user = user_crud.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT with user info in payload
    token = create_access_token({
        "id": user.id,
        "email": user.email,
        "role": user.role
    })

    return Token(
        access_token=token,
        token_type="bearer",
        user=user
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user profile.
    Depends(get_current_user) handles JWT verification automatically.
    """
    return current_user


@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    current_user: User = Depends(require_admin),  # admin only
    db: Session = Depends(get_db)
):
    """Get all users — admin only."""
    return user_crud.get_all_users(db)