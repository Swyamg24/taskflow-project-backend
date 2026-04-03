from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.auth.jwt import verify_token
from app.crud import user_crud
from app.models import User

# HTTPBearer extracts the JWT from "Authorization: Bearer <token>" header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that:
    1. Extracts JWT from Authorization header
    2. Verifies the token
    3. Looks up user in DB
    4. Returns the User object

    Usage: current_user: User = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = verify_token(credentials.credentials)
    except JWTError:
        raise credentials_exception

    user = user_crud.get_user_by_id(db, user_id=token_data.id)
    if user is None:
        raise credentials_exception

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that requires admin role.
    Usage: current_user: User = Depends(require_admin)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user