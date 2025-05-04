from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Tasks, ScheduleSlot, UserPreferences
from datetime import datetime, timedelta, time
import google.generativeai as genai
import os

router = APIRouter(
    prefix="/planner",
    tags=["Planner"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#ddf
db_dependency = Annotated[Session, Depends(get_db)]

# Load Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def call_gemini_for_schedule(tasks, user_notes):
    task_descriptions = "\n".join([f"- {task.title}: {task.description or 'No description'} (Priority: {task.priority})"
                                   for task in tasks])

    prompt = f"""
You are a smart schedule assistant for a high school student preparing for exams.
Based on the following tasks and user preferences, create a one-week schedule plan.
Try to respect task deadlines and priorities.

USER NOTES:
{user_notes}

TASKS:
{task_descriptions}

Output the plan as a JSON list with this format:
[
    {{
        "title": "Task Title",
        "day": "Monday",
        "start_time": "10:00",
        "end_time": "11:30"
    }},
    ...
]
"""

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    try:
        plan_json = eval(response.text)  # NOTE: Replace with `json.loads()` if response is strict JSON
        return plan_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini response parsing failed: {str(e)}")


@router.post("/auto-schedule/{user_id}")
def generate_ai_schedule(user_id: int, user_notes: str, db: Session = Depends(get_db)):
    # Get tasks for user
    tasks = db.query(Tasks).filter(Tasks.owner_id == user_id, Tasks.completed == False).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for user.")

    # Call Gemini AI
    ai_plan = call_gemini_for_schedule(tasks, user_notes)

    # Clear previous plan
    db.query(ScheduleSlot).filter(ScheduleSlot.user_id == user_id).delete()

    for item in ai_plan:
        start_hour, start_minute = map(int, item["start_time"].split(":"))
        end_hour, end_minute = map(int, item["end_time"].split(":"))

        schedule = ScheduleSlot(
            user_id=user_id,
            day=item["day"],
            start_time=time(start_hour, start_minute),
            end_time=time(end_hour, end_minute),
            task_id=next((t.id for t in tasks if t.title == item["title"]), None)
        )
        db.add(schedule)

    db.commit()
    return {"message": "Schedule created successfully from Gemini AI."}


@router.get("/manual-mode/{user_id}")
def get_tasks_for_manual_mode(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Tasks).filter(Tasks.owner_id == user_id, Tasks.completed == False).all()
    return tasks
