from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import router as auth_router
from controllers.categories import router as categories_router
from controllers.reminders import router as reminders_router
from controllers.tags import router as tags_router
from controllers.tasks import router as tasks_router
from controllers.users import router as users_router

app = FastAPI(
    title="Time Manager API",
    description=(
        "Учебный серверный проект для управления задачами, категориями, тегами "
        "и напоминаниями."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(reminders_router)


@app.get("/")
def read_root():
    return {
        "project": "Time Manager API",
        "message": "Service is ready. Run Alembic migrations before using the API.",
    }
