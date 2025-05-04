from fastapi import APIRouter, Depends, Path, HTTPException, Request
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from models import Base, Tasks, Analyzer, Mistake, User
from database import engine, SessionLocal
from typing import Annotated
from pydantic import BaseModel, Field
from routers.auth import get_current_user, templates
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import markdown
from bs4 import BeautifulSoup




router = APIRouter()


templates = Jinja2Templates(directory="app/templates")

class TaskCreate(BaseModel):
    title: str = Field(..., example="Task Title")
    description: str = Field(..., example="Task Description")
    priority: int = Field(..., example=1)
    deadline: str = Field(..., example="2023-12-31")
    completed: bool = Field(False, example=False)
    estimated_time: str = Field(..., example="2 hours")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#ddf
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Tasks).filter(Tasks.owner_id == user.get('id')).all()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(user: user_dependency, db: db_dependency, task_request: TaskCreate):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    tasks = Tasks (**task_request.dict(), owner_id=user.get('id'))
    db.add(tasks)
    db.commit()


@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.owner_id == user["id"]).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

@router.put("/task/{task_id}", status_code=status.HTTP_200_OK)
async def update_study_task(
    task_id: int,
    task_update: TaskCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.owner_id == user["id"]).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = task_update.title
    task.description = task_update.description
    task.priority = task_update.priority
    task.deadline = task_update.deadline
    task.completed = task_update.completed

    db.commit()
    return {"message": "Task updated"}



