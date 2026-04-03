from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime


# ── USER SCHEMAS ─────────────────────────────────────────────

class UserCreate(BaseModel):
    """Schema for POST /auth/register request body"""
    name: str
    email: EmailStr          # Pydantic validates email format automatically
    password: str

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class UserResponse(BaseModel):
    """Schema for responses — never includes password"""
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model objects


class UserLogin(BaseModel):
    """Schema for POST /auth/login"""
    email: EmailStr
    password: str


# ── TOKEN SCHEMAS ─────────────────────────────────────────────

class Token(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Data stored inside JWT payload"""
    id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


# ── TASK SCHEMAS ──────────────────────────────────────────────

class TaskCreate(BaseModel):
    """Schema for POST /tasks"""
    title: str
    description: Optional[str] = None

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class TaskUpdate(BaseModel):
    """Schema for PUT /tasks/{id} — all fields optional"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal['pending', 'in_progress', 'done']] = None


class TaskResponse(BaseModel):
    """Schema for task responses"""
    id: int
    title: str
    description: Optional[str]
    status: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True