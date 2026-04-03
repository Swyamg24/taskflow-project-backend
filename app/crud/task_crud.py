from sqlalchemy.orm import Session, joinedload
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


def create_task(db: Session, task_data: TaskCreate, owner_id: int):
    task = Task(
        title=task_data.title,
        description=task_data.description,
        owner_id=owner_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(db: Session, user_id: int, role: str):
    """Admin sees all tasks; users see only their own."""
    if role == "admin":
        return db.query(Task).order_by(Task.created_at.desc()).all()
    return (
        db.query(Task)
        .filter(Task.owner_id == user_id)
        .order_by(Task.created_at.desc())
        .all()
    )


def get_task_by_id(db: Session, task_id: int, user_id: int, role: str):
    """Fetch single task — admin can see any, users only their own."""
    query = db.query(Task).filter(Task.id == task_id)
    if role != "admin":
        query = query.filter(Task.owner_id == user_id)
    return query.first()


def update_task(db: Session, task_id: int, user_id: int, role: str, update_data: TaskUpdate):
    task = get_task_by_id(db, task_id, user_id, role)
    if not task:
        return None

    # Only update fields that were actually provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user_id: int, role: str):
    task = get_task_by_id(db, task_id, user_id, role)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True