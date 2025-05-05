from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models import LessonPerformanceSummary
from routers.auth import get_current_user
from routers.analyzer import check_user, get_db

router = APIRouter()

class LessonPerformanceSummarySchema(BaseModel):
    lesson_id: int
    user_id: int
    total_questions: int
    correct: int
    wrong: int
    blank: int
    total_time: int


@router.get("/user/lesson-performance", response_model=list[LessonPerformanceSummarySchema])  # response_model'ı model olarak ayarlıyoruz
async def get_user_lesson_performance(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    check_user(user)

    # Kullanıcıya ait tüm ders performanslarını getir
    results = db.query(LessonPerformanceSummary).filter(
        LessonPerformanceSummary.user_id == user["id"]
    ).all()

    return results
