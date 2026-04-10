from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth.auth import auth_service
from connection import get_session
from models import (
    ApiMessage,
    Reminder,
    ReminderCreate,
    ReminderRead,
    ReminderUpdate,
    Task,
    User,
)

router = APIRouter(prefix="/reminders", tags=["reminders"])


def get_owned_task(task_id: int, db_session: Session, current_user: User) -> Task:
    task_record = db_session.get(Task, task_id)
    if not task_record or task_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_record


def get_owned_reminder(
    reminder_id: int,
    db_session: Session,
    current_user: User,
) -> Reminder:
    reminder_record = db_session.get(Reminder, reminder_id)
    if not reminder_record:
        raise HTTPException(status_code=404, detail="Reminder not found")

    get_owned_task(reminder_record.task_id, db_session, current_user)
    return reminder_record


@router.post("/", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(
    reminder_data: ReminderCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ReminderRead:
    get_owned_task(reminder_data.task_id, db_session, current_user)

    reminder_record = Reminder(**reminder_data.model_dump())
    db_session.add(reminder_record)
    db_session.commit()
    db_session.refresh(reminder_record)
    return ReminderRead(**reminder_record.model_dump())


@router.get("/", response_model=list[ReminderRead])
def read_reminders(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> list[ReminderRead]:
    reminder_records = db_session.exec(
        select(Reminder)
        .join(Task)
        .where(Task.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return [ReminderRead(**reminder.model_dump()) for reminder in reminder_records]


@router.get("/{reminder_id}", response_model=ReminderRead)
def read_reminder(
    reminder_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ReminderRead:
    reminder_record = get_owned_reminder(reminder_id, db_session, current_user)
    return ReminderRead(**reminder_record.model_dump())


@router.patch("/{reminder_id}", response_model=ReminderRead)
def update_reminder(
    reminder_id: int,
    reminder_data: ReminderUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ReminderRead:
    reminder_record = get_owned_reminder(reminder_id, db_session, current_user)
    update_payload = reminder_data.model_dump(exclude_unset=True)

    if not update_payload:
        raise HTTPException(status_code=400, detail="No data provided for update")

    new_task_id = update_payload.get("task_id")
    if new_task_id is not None:
        get_owned_task(new_task_id, db_session, current_user)

    for field_name, field_value in update_payload.items():
        setattr(reminder_record, field_name, field_value)

    db_session.add(reminder_record)
    db_session.commit()
    db_session.refresh(reminder_record)
    return ReminderRead(**reminder_record.model_dump())


@router.delete("/{reminder_id}", response_model=ApiMessage)
def delete_reminder(
    reminder_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ApiMessage:
    reminder_record = get_owned_reminder(reminder_id, db_session, current_user)
    db_session.delete(reminder_record)
    db_session.commit()
    return ApiMessage(message="Reminder deleted successfully")
