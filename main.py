from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
from database import engine, Base
from routers import (
    auth, tasks, chatbot, planner, analyzer, user_analytics
)

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root(request: Request):
    return RedirectResponse(url="/tasks/tasks-page", status_code=status.HTTP_302_FOUND)


# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(planner.router, prefix="/planner", tags=["Planner"])
app.include_router(analyzer.router, prefix="/analyzer", tags=["Analyzer"])
app.include_router(user_analytics.router, prefix="/user_analytics", tags=["User Analytics"])
