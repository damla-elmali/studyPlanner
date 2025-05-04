from fastapi import FastAPI


from database import engine, Base
from routers import (
    auth, tasks, chatbot, planner, analyzer, mistakes, lessons, topics
)

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(title="Study Planner App", version="1.0")


# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(planner.router, prefix="/planner", tags=["Planner"])
app.include_router(analyzer.router, prefix="/analyzer", tags=["Analyzer"])

