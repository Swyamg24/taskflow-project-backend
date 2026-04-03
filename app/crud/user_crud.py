from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from app.auth.hashing import hash_password, verify_password


def get_user_by_email(db: Session, email: str):
    """SELECT * FROM users WHERE email = :email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """SELECT * FROM users WHERE id = :id"""
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session):
    """SELECT * FROM users — admin only"""
    return db.query(User).order_by(User.created_at.desc()).all()


def create_user(db: Session, user_data: UserCreate, role: str = "user"):
    """
    INSERT INTO users (...) VALUES (...)
    Hashes password before saving.
    """
    hashed = hash_password(user_data.password)
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed,
        role=role,
    )
    db.add(db_user)       # stages the insert
    db.commit()           # executes the SQL
    db.refresh(db_user)   # reloads from DB (gets auto-generated id, timestamps)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    """
    Find user by email, then verify password.
    Returns user if valid, None if not.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user