from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Tasks, ScheduleSlot
from datetime import datetime, time
from routers.auth import get_current_user
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
import google.generativeai as genai

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ManualPlanRequest(BaseModel):
    task: str
    startTime: str
    endTime: str

class UpdatePlanRequest(BaseModel):
    startTime: str
    endTime: str

class AIPlanRequest(BaseModel):
    user_notes: str = "User prefers to study in the evenings."


@router.get("/plan")
async def get_plans(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    plans = db.query(ScheduleSlot).filter(ScheduleSlot.user_id == user["id"]).all()
    return plans


@router.put("/plan/{slot_id}")
async def update_plan(slot_id: int, request: UpdatePlanRequest, db: Session = Depends(get_db),
                user: dict = Depends(get_current_user)):
    slot = db.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id, ScheduleSlot.user_id == user["id"]).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Plan not found")

    start_time = datetime.fromisoformat(request.startTime)
    end_time = datetime.fromisoformat(request.endTime)

    slot.start_time = start_time.time()
    slot.end_time = end_time.time()
    db.commit()

    return {"message": "Plan updated successfully"}


@router.delete("/plan/{slot_id}")
async def delete_plan(slot_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    slot = db.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id, ScheduleSlot.user_id == user["id"]).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Plan not found")

    db.delete(slot)
    db.commit()
    return {"message": "Plan deleted successfully"}


@router.post("/plan/manual")
async def manual_plan(request: ManualPlanRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    task = db.query(Tasks).filter(Tasks.title == request.task, Tasks.owner_id == user["id"]).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_deadline = datetime.strptime(task.deadline, "%Y-%m-%d")
    start_time = datetime.fromisoformat(request.startTime)
    end_time = datetime.fromisoformat(request.endTime)

    if end_time > task_deadline:
        raise HTTPException(status_code=400, detail="Plan cannot extend beyond the task's deadline.")

    overlapping = db.query(ScheduleSlot).filter(
        ScheduleSlot.user_id == user["id"],
        ScheduleSlot.start_time <= end_time.time(),
        ScheduleSlot.end_time >= start_time.time()
    ).first()

    if overlapping:
        raise HTTPException(status_code=409, detail="Time slot overlaps with an existing plan.")

    slot = ScheduleSlot(
        user_id=user["id"],
        task_id=task.id,
        day=start_time.strftime('%A'),
        start_time=start_time.time(),
        end_time=end_time.time()
    )
    db.add(slot)
    db.commit()

    google_calendar_link = generate_google_calendar_link({
        'title': task.title,
        'start_time': start_time,
        'end_time': end_time,
        'description': f"Manual study session for {task.title}",
    })

    return {"message": "Manual schedule created.", "google_calendar_link": google_calendar_link}


@router.post("/plan/ai")
async def ai_plan(request: AIPlanRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    tasks = db.query(Tasks).filter(Tasks.owner_id == user["id"], Tasks.completed == False).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for user.")

    plan = call_gemini_for_schedule(tasks, request.user_notes)

    for item in plan:
        start_hour, start_minute = map(int, item["start_time"].split(":"))
        end_hour, end_minute = map(int, item["end_time"].split(":"))
        task = next((t for t in tasks if t.title == item["title"]), None)

        if task:
            task_deadline = datetime.strptime(task.deadline, "%Y-%m-%d")
            event_start = datetime.combine(datetime.today(), time(start_hour, start_minute))
            event_end = datetime.combine(datetime.today(), time(end_hour, end_minute))

            if event_end > task_deadline:
                raise HTTPException(status_code=400, detail="AI plan cannot extend beyond the task's deadline.")

            slot = ScheduleSlot(
                user_id=user["id"],
                task_id=task.id,
                day=item["day"],
                start_time=time(start_hour, start_minute),
                end_time=time(end_hour, end_minute)
            )
            db.add(slot)

            google_calendar_link = generate_google_calendar_link({
                'title': task.title,
                'start_time': event_start,
                'end_time': event_end,
                'description': f"AI-planned session for {task.title}",
            })

            return {"message": "AI-based schedule created.", "google_calendar_link": google_calendar_link}

    db.commit()
    return {"message": "AI-based schedule created."}


def call_gemini_for_schedule(tasks, user_notes):
    load_dotenv()
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

    task_descriptions = "\n".join(
        [f"- {task.title}: {task.description or 'No description'} (Priority: {task.priority})" for task in tasks]
    )

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
        plan_json = eval(response.text)
        return plan_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini response parsing failed: {str(e)}")


def generate_google_calendar_link(event_details):
    base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
    event_data = {
        "text": event_details['title'],
        "dates": f"{event_details['start_time'].isoformat()}Z/{event_details['end_time'].isoformat()}Z",
        "details": event_details.get('description', ''),
    }
    event_url = base_url + '&' + '&'.join([f"{key}={quote_plus(value)}" for key, value in event_data.items()])
    return event_url
