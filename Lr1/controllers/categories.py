from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth.auth import auth_service
from connection import get_session
from models import (
    ApiMessage,
    TaskCategory,
    TaskCategoryCreate,
    TaskCategoryRead,
    TaskCategoryUpdate,
    User,
)

router = APIRouter(prefix="/categories", tags=["categories"])


def get_owned_category(
    category_id: int,
    db_session: Session,
    current_user: User,
) -> TaskCategory:
    category_record = db_session.get(TaskCategory, category_id)
    if not category_record or category_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return category_record


@router.post("/", response_model=TaskCategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: TaskCategoryCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TaskCategoryRead:
    category_record = TaskCategory(**category_data.model_dump(), user_id=current_user.id)
    db_session.add(category_record)
    db_session.commit()
    db_session.refresh(category_record)
    return TaskCategoryRead(**category_record.model_dump())


@router.get("/", response_model=list[TaskCategoryRead])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> list[TaskCategoryRead]:
    category_records = db_session.exec(
        select(TaskCategory)
        .where(TaskCategory.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return [TaskCategoryRead(**category.model_dump()) for category in category_records]


@router.get("/{category_id}", response_model=TaskCategoryRead)
def read_category(
    category_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TaskCategoryRead:
    category_record = get_owned_category(category_id, db_session, current_user)
    return TaskCategoryRead(**category_record.model_dump())


@router.patch("/{category_id}", response_model=TaskCategoryRead)
def update_category(
    category_id: int,
    category_data: TaskCategoryUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TaskCategoryRead:
    category_record = get_owned_category(category_id, db_session, current_user)
    update_payload = category_data.model_dump(exclude_unset=True)

    if not update_payload:
        raise HTTPException(status_code=400, detail="No data provided for update")

    for field_name, field_value in update_payload.items():
        setattr(category_record, field_name, field_value)

    db_session.add(category_record)
    db_session.commit()
    db_session.refresh(category_record)
    return TaskCategoryRead(**category_record.model_dump())


@router.delete("/{category_id}", response_model=ApiMessage)
def delete_category(
    category_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ApiMessage:
    category_record = get_owned_category(category_id, db_session, current_user)
    db_session.delete(category_record)
    db_session.commit()
    return ApiMessage(message="Category deleted successfully")
