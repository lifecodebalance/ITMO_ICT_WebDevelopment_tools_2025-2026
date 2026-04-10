from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth.auth import auth_service
from connection import get_session
from models import (
    ApiMessage,
    Tag,
    TagRead,
    Task,
    TaskCategory,
    TaskCreate,
    TaskRead,
    TaskTag,
    TaskUpdate,
    TaskWithTagsRead,
    User,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_owned_task(task_id: int, db_session: Session, current_user: User) -> Task:
    task_record = db_session.get(Task, task_id)
    if not task_record or task_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_record


def validate_category_access(
    category_id: int | None,
    db_session: Session,
    current_user: User,
) -> None:
    if category_id is None:
        return

    category_record = db_session.get(TaskCategory, category_id)
    if not category_record or category_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")


def build_task_view(task_record: Task, db_session: Session) -> TaskWithTagsRead:
    tag_records = db_session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == task_record.id)
    ).all()

    # Здесь вложенные теги собираются вручную.
    # Так проще показать новичку, как формируется расширенный DTO для ответа API.
    return TaskWithTagsRead(
        **task_record.model_dump(),
        tags=[TagRead(**tag.model_dump()) for tag in tag_records],
    )


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TaskRead:
    validate_category_access(task_data.category_id, db_session, current_user)

    task_record = Task(**task_data.model_dump(), user_id=current_user.id)
    db_session.add(task_record)
    db_session.commit()
    db_session.refresh(task_record)
    return TaskRead(**task_record.model_dump())


@router.get("/", response_model=list[TaskWithTagsRead])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> list[TaskWithTagsRead]:
    task_records = db_session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return [build_task_view(task_record, db_session) for task_record in task_records]


@router.get("/{task_id}", response_model=TaskWithTagsRead)
def read_task(
    task_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TaskWithTagsRead:
    task_record = get_owned_task(task_id, db_session, current_user)
    return build_task_view(task_record, db_session)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TaskRead:
    task_record = get_owned_task(task_id, db_session, current_user)
    update_payload = task_data.model_dump(exclude_unset=True)

    if not update_payload:
        raise HTTPException(status_code=400, detail="No data provided for update")

    validate_category_access(update_payload.get("category_id"), db_session, current_user)

    for field_name, field_value in update_payload.items():
        setattr(task_record, field_name, field_value)

    db_session.add(task_record)
    db_session.commit()
    db_session.refresh(task_record)
    return TaskRead(**task_record.model_dump())


@router.delete("/{task_id}", response_model=ApiMessage)
def delete_task(
    task_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ApiMessage:
    task_record = get_owned_task(task_id, db_session, current_user)
    db_session.delete(task_record)
    db_session.commit()
    return ApiMessage(message="Task deleted successfully")


@router.post("/{task_id}/tags/{tag_id}", response_model=ApiMessage)
def add_tag_to_task(
    task_id: int,
    tag_id: int,
    is_primary: bool = False,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ApiMessage:
    get_owned_task(task_id, db_session, current_user)

    tag_record = db_session.get(Tag, tag_id)
    if not tag_record or tag_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    link_record = TaskTag(task_id=task_id, tag_id=tag_id, is_primary=is_primary)
    db_session.add(link_record)

    try:
        db_session.commit()
    except IntegrityError as exc:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Tag is already attached to task") from exc

    return ApiMessage(message="Tag added to task successfully")


@router.delete("/{task_id}/tags/{tag_id}", response_model=ApiMessage)
def remove_tag_from_task(
    task_id: int,
    tag_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ApiMessage:
    get_owned_task(task_id, db_session, current_user)

    tag_record = db_session.get(Tag, tag_id)
    if not tag_record or tag_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    link_record = db_session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id)
    ).first()

    if not link_record:
        raise HTTPException(status_code=404, detail="Tag not found on task")

    db_session.delete(link_record)
    db_session.commit()
    return ApiMessage(message="Tag removed from task successfully")
