from passlib.context import CryptContext

# CryptContext handles hashing schemes; bcrypt is the gold standard
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convert plain password → bcrypt hash"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare plain text with hash — returns True if match"""
    return pwd_context.verify(plain_password, hashed_password)