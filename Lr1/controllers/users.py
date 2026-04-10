from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth.auth import auth_service
from connection import get_session
from models import (
    Reminder,
    ReminderRead,
    Tag,
    TagRead,
    Task,
    TaskCategory,
    TaskCategoryRead,
    TaskRead,
    User,
    UserDetailsRead,
    UserListItem,
    UserRead,
)

router = APIRouter(prefix="/users", tags=["users"])


def build_user_details(user_record: User, db_session: Session) -> UserDetailsRead:
    task_records = db_session.exec(
        select(Task).where(Task.user_id == user_record.id)
    ).all()
    category_records = db_session.exec(
        select(TaskCategory).where(TaskCategory.user_id == user_record.id)
    ).all()
    tag_records = db_session.exec(
        select(Tag).where(Tag.user_id == user_record.id)
    ).all()
    reminder_records = db_session.exec(
        select(Reminder).join(Task).where(Task.user_id == user_record.id)
    ).all()

    return UserDetailsRead(
        id=user_record.id,
        username=user_record.username,
        email=user_record.email,
        created_at=user_record.created_at,
        tasks=[TaskRead(**task.model_dump()) for task in task_records],
        categories=[
            TaskCategoryRead(**category.model_dump()) for category in category_records
        ],
        tags=[TagRead(**tag.model_dump()) for tag in tag_records],
        reminders=[ReminderRead(**reminder.model_dump()) for reminder in reminder_records],
    )


def ensure_same_user(requested_user_id: int, current_user: User) -> None:
    if requested_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile details",
        )


@router.get("/", response_model=list[UserListItem])
def get_all_users(
    current_user: User = Depends(auth_service.get_current_user),
) -> list[UserListItem]:
    # Скрываем остальных пользователей: в списке доступен только текущий пользователь.
    return [
        UserListItem(
            id=current_user.id,
            username=current_user.username,
            created_at=current_user.created_at,
        )
    ]


@router.get("/me/details", response_model=UserDetailsRead)
def get_current_user_details(
    current_user: User = Depends(auth_service.get_current_user),
    db_session: Session = Depends(get_session),
) -> UserDetailsRead:
    user_record = db_session.get(User, current_user.id)
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    return build_user_details(user_record, db_session)


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db_session: Session = Depends(get_session),
) -> UserRead:
    ensure_same_user(user_id, current_user)

    user_record = db_session.get(User, user_id)
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    return UserRead(
        id=user_record.id,
        username=user_record.username,
        email=user_record.email,
        created_at=user_record.created_at,
    )


@router.get("/{user_id}/details", response_model=UserDetailsRead)
def get_user_details_by_id(
    user_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db_session: Session = Depends(get_session),
) -> UserDetailsRead:
    ensure_same_user(user_id, current_user)

    user_record = db_session.get(User, user_id)
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    return build_user_details(user_record, db_session)
