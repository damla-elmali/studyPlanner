from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import engine, SessionLocal
from routers.auth import get_current_user
from models import UserPreferences, Tasks, ScheduleSlot
from datetime import datetime, time, timedelta
from pydantic import BaseModel, Field
import calendar

router = APIRouter()


class PlannerRequest(BaseModel):
    preferred_start_hour: Optional[int] = Field(ge=0, le=23, description="Start hour of planning window (0-23)")
    preferred_end_hour: Optional[int] = Field(ge=0, le=23, description="End hour of planning window (0-23)")
    preferred_days: Optional[List[str]] = Field(
        default=["Mon", "Tue", "Wed", "Thu", "Fri"],
        description="Days to plan tasks, e.g., ['Mon', 'Wed', 'Fri']"
    )
    task_duration_hours: Optional[int] = Field(default=1, gt=0, le=8, description="Duration of each task slot in hours")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/auto-plan", status_code=status.HTTP_201_CREATED)
def auto_generate_plan(
    request: Optional[PlannerRequest] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_id = user["id"]

    preferences = db.query(UserPreferences).filter_by(user_id=user_id).first()
    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found.")

    tasks = db.query(Tasks).filter_by(owner_id=user_id, completed=False).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks to schedule.")

    # Clear previous auto-generated slots
    db.query(ScheduleSlot).filter_by(user_id=user_id).delete()

    # Use request if given, otherwise fallback to saved preferences
    start_hour = request.preferred_start_hour if request and request.preferred_start_hour is not None else preferences.preferred_start_hour
    end_hour = request.preferred_end_hour if request and request.preferred_end_hour is not None else preferences.preferred_end_hour
    preferred_days = request.preferred_days if request and request.preferred_days else preferences.preferred_days.split(",")
    task_duration = timedelta(hours=request.task_duration_hours) if request and request.task_duration_hours else timedelta(hours=1)

    plan = generate_weekly_plan(user_id, preferred_days, start_hour, end_hour, tasks, task_duration)

    for slot in plan:
        db.add(slot)
    db.commit()

    return {"message": "Plan created", "slots_created": len(plan)}


@router.get("/schedule", response_model=List[dict])
def get_schedule(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    schedule = db.query(ScheduleSlot).filter_by(user_id=user["id"]).all()
    return [
        {
            "day": s.day,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "task_title": s.task.title if s.task else None
        }
        for s in schedule
    ]


@router.post("/preferences", status_code=status.HTTP_201_CREATED)
def set_preferences(
    preferred_start_hour: int,
    preferred_end_hour: int,
    preferred_days: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    existing = db.query(UserPreferences).filter_by(user_id=user["id"]).first()
    if existing:
        existing.preferred_start_hour = preferred_start_hour
        existing.preferred_end_hour = preferred_end_hour
        existing.preferred_days = preferred_days
    else:
        new_pref = UserPreferences(
            user_id=user["id"],
            preferred_start_hour=preferred_start_hour,
            preferred_end_hour=preferred_end_hour,
            preferred_days=preferred_days,
        )
        db.add(new_pref)

    db.commit()
    return {"message": "Preferences saved"}


def generate_weekly_plan(user_id, preferred_days, start_hour, end_hour, tasks, task_duration):
    slots = []

    # Map short day names to full
    day_map = dict(zip(calendar.day_abbr, calendar.day_name))
    days_full = [day_map.get(day[:3]) for day in preferred_days if day[:3] in day_map]

    task_index = 0

    for day in days_full:
        current_time = time(hour=start_hour)
        while datetime.combine(datetime.today(), current_time).time() < time(hour=end_hour):
            if task_index >= len(tasks):
                break

            task = tasks[task_index]
            end_time = (datetime.combine(datetime.today(), current_time) + task_duration).time()

            slots.append(ScheduleSlot(
                user_id=user_id,
                day=day,
                start_time=current_time,
                end_time=end_time,
                task_id=task.id
            ))

            # Increment task
            task_index += 1
            current_time = (datetime.combine(datetime.today(), current_time) + task_duration).time()

    return slots
