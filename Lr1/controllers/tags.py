from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth.auth import auth_service
from connection import get_session
from models import ApiMessage, Tag, TagCreate, TagRead, TagUpdate, User

router = APIRouter(prefix="/tags", tags=["tags"])


def get_owned_tag(tag_id: int, db_session: Session, current_user: User) -> Tag:
    tag_record = db_session.get(Tag, tag_id)
    if not tag_record or tag_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag_record


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TagRead:
    tag_record = Tag(**tag_data.model_dump(), user_id=current_user.id)
    db_session.add(tag_record)
    db_session.commit()
    db_session.refresh(tag_record)
    return TagRead(**tag_record.model_dump())


@router.get("/", response_model=list[TagRead])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> list[TagRead]:
    tag_records = db_session.exec(
        select(Tag).where(Tag.user_id == current_user.id).offset(skip).limit(limit)
    ).all()
    return [TagRead(**tag.model_dump()) for tag in tag_records]


@router.get("/{tag_id}", response_model=TagRead)
def read_tag(
    tag_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TagRead:
    tag_record = get_owned_tag(tag_id, db_session, current_user)
    return TagRead(**tag_record.model_dump())


@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> TagRead:
    tag_record = get_owned_tag(tag_id, db_session, current_user)
    update_payload = tag_data.model_dump(exclude_unset=True)

    if not update_payload:
        raise HTTPException(status_code=400, detail="No data provided for update")

    for field_name, field_value in update_payload.items():
        setattr(tag_record, field_name, field_value)

    db_session.add(tag_record)
    db_session.commit()
    db_session.refresh(tag_record)
    return TagRead(**tag_record.model_dump())


@router.delete("/{tag_id}", response_model=ApiMessage)
def delete_tag(
    tag_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> ApiMessage:
    tag_record = get_owned_tag(tag_id, db_session, current_user)
    db_session.delete(tag_record)
    db_session.commit()
    return ApiMessage(message="Tag deleted successfully")
