from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class ApiMessage(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    categories: list["TaskCategory"] = Relationship(back_populates="user")
    tasks: list["Task"] = Relationship(back_populates="user")
    tags: list["Tag"] = Relationship(back_populates="user")


class UserRegister(SQLModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    created_at: datetime


class UserListItem(SQLModel):
    id: int
    username: str
    created_at: datetime


class TaskCategoryBase(SQLModel):
    name: str = Field(index=True)
    color_code: str = Field(default="#FFFFFF")


class TaskCategoryCreate(TaskCategoryBase):
    pass


class TaskCategoryUpdate(SQLModel):
    name: str | None = None
    color_code: str | None = None


class TaskCategory(TaskCategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates="categories")
    tasks: list["Task"] = Relationship(back_populates="category")


class TaskCategoryRead(TaskCategoryBase):
    id: int
    user_id: int


class TagBase(SQLModel):
    name: str = Field(index=True)


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: str | None = None


class TaskTagBase(SQLModel):
    task_id: int = Field(foreign_key="task.id")
    tag_id: int = Field(foreign_key="tag.id")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    is_primary: bool = False


class TaskTag(TaskTagBase, table=True):
    # Ассоциативная таблица не только связывает задачу и тег,
    # но и хранит полезные данные о самой связи.
    __tablename__ = "tasktag"

    task_id: int = Field(primary_key=True, foreign_key="task.id")
    tag_id: int = Field(primary_key=True, foreign_key="tag.id")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    is_primary: bool = False


class Tag(TagBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates="tags")
    tasks: list["Task"] = Relationship(back_populates="tags", link_model=TaskTag)


class TagRead(TagBase):
    id: int
    user_id: int


class TaskBase(SQLModel):
    title: str = Field(index=True)
    description: str
    deadline: datetime | None = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.todo
    estimated_time_minutes: int = 0
    actual_time_minutes: int = 0


class TaskCreate(TaskBase):
    category_id: int | None = None


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    estimated_time_minutes: int | None = None
    actual_time_minutes: int | None = None
    category_id: int | None = None


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    user_id: int = Field(foreign_key="user.id")
    category_id: int | None = Field(default=None, foreign_key="taskcategory.id")

    user: User = Relationship(back_populates="tasks")
    category: "TaskCategory" = Relationship(back_populates="tasks")
    tags: list["Tag"] = Relationship(back_populates="tasks", link_model=TaskTag)
    reminders: list["Reminder"] = Relationship(back_populates="task")


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    user_id: int
    category_id: int | None


class ReminderBase(SQLModel):
    remind_at: datetime
    is_sent: bool = False


class ReminderCreate(ReminderBase):
    task_id: int


class ReminderUpdate(SQLModel):
    remind_at: datetime | None = None
    is_sent: bool | None = None
    task_id: int | None = None


class Reminder(ReminderBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")

    task: Task = Relationship(back_populates="reminders")


class ReminderRead(ReminderBase):
    id: int
    task_id: int


class TaskWithTagsRead(TaskRead):
    tags: list[TagRead] = Field(default_factory=list)


class UserDetailsRead(UserRead):
    # В подробном профиле явно разворачиваем связанные сущности,
    # чтобы в документации и ответах API было видно структуру данных.
    tasks: list[TaskRead] = Field(default_factory=list)
    categories: list[TaskCategoryRead] = Field(default_factory=list)
    tags: list[TagRead] = Field(default_factory=list)
    reminders: list[ReminderRead] = Field(default_factory=list)
