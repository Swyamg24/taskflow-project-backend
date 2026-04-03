from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.crud import task_crud
from app.auth.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks. Users see their own; admins see all."""
    return task_crud.get_tasks(db, current_user.id, current_user.role)


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task for the current user."""
    return task_crud.create_task(db, task_data, current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = task_crud.get_task_by_id(db, task_id, current_user.id, current_user.role)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    update_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = task_crud.update_task(db, task_id, current_user.id, current_user.role, update_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleted = task_crud.delete_task(db, task_id, current_user.id, current_user.role)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    # 204 No Content — no response body