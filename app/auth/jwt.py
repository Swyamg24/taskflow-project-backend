from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.schemas import TokenData
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))


def create_access_token(data: dict) -> str:
    """
    Create a JWT token.
    data = {"id": 1, "email": "...", "role": "user"}
    Returns signed token string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # "exp" = expiry claim — JWT standard

    # jwt.encode = signs the payload with SECRET_KEY using ALGORITHM
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> TokenData:
    """
    Decode and verify JWT.
    Raises JWTError if invalid or expired.
    Returns TokenData with user info from payload.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: int = payload.get("id")
    email: str = payload.get("email")
    role: str = payload.get("role")

    if user_id is None:
        raise JWTError("Invalid token payload")

    return TokenData(id=user_id, email=email, role=role)